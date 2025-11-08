package main

import (
	"bytes"
	"context"
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"brabocker/db"

	_ "embed"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

//go:embed schema.sql
var schemaSQL string

//go:embed init.sql
var initSQL string

type server struct {
	templates *template.Template
	db        *sql.DB
}

func (s *server) withQueries(ctx context.Context, f func(*db.Queries) error) error {
	conn, err := s.db.Conn(ctx)
	if err != nil {
		return err
	}
	defer conn.Close()

	queries := db.New(conn)
	return f(queries)
}

func (s *server) index(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte("Not Found!"))
		return
	}

	user, ok := r.Context().Value("user").(User)
	if !ok {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		log.Println("Failed type assertion")
		return
	}

	var reviews []db.GetReviewsRow
	if err := s.withQueries(r.Context(), func(queries *db.Queries) error {
		var err error
		reviews, err = queries.GetReviews(r.Context())
		return err
	}); err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("%v", err)
		return
	}

	s.templates.ExecuteTemplate(w, "index.html", struct {
		Reviews []db.GetReviewsRow
		User    User
	}{Reviews: reviews, User: user})
}

func (s *server) review(w http.ResponseWriter, r *http.Request) {
	args, err := url.ParseQuery(r.URL.RawQuery)
	if err != nil {
		http.Error(w, "Invalid query arguments", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	id, err := strconv.Atoi(args.Get("id"))
	if err != nil {
		http.Error(w, "Invalid id", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	var review db.GetReviewRow
	var comments []db.GetCommentsRow
	if err := s.withQueries(r.Context(), func(queries *db.Queries) error {
		var err error
		review, err = queries.GetReview(r.Context(), int64(id))
		if err != nil {
			return err
		}
		comments, err = queries.GetComments(r.Context(), int64(id))
		return err
	}); err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("%v", err)
		return
	}

	s.templates.ExecuteTemplate(w, "review.html", struct {
		Review   db.GetReviewRow
		Comments []db.GetCommentsRow
	}{Review: review, Comments: comments})
}

func (s *server) withTx(ctx context.Context, f func(*db.Queries) error) error {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	queries := db.New(tx)
	if err := f(queries); err != nil {
		return err
	}

	return tx.Commit()
}

func (s *server) comment(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		args, err := url.ParseQuery(r.URL.RawQuery)
		if err != nil {
			http.Error(w, "Invalid query arguments", http.StatusBadRequest)
			log.Printf("%v", err)
			return
		}

		id, err := strconv.Atoi(args.Get("id"))
		if err != nil {
			http.Error(w, "Invalid id", http.StatusBadRequest)
			log.Printf("%v", err)
			return
		}

		var review db.GetReviewRow
		if err := s.withQueries(r.Context(), func(queries *db.Queries) error {
			var err error
			review, err = queries.GetReview(r.Context(), int64(id))
			return err
		}); err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			log.Printf("%v", err)
			return
		}

		s.templates.ExecuteTemplate(w, "comment.html", review)
		return
	}

	user, ok := r.Context().Value("user").(User)
	if !ok {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		log.Println("Failed type assertion")
		return
	}

	if err := r.ParseForm(); err != nil {
		http.Error(w, "Invalid form", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	reviewId, err := strconv.Atoi(r.PostFormValue("review_id"))
	if err != nil {
		http.Error(w, "Invalid review_id", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	if err := s.withTx(r.Context(), func(queries *db.Queries) error {
		return queries.CreateComment(r.Context(), db.CreateCommentParams{
			ReviewID: int64(reviewId),
			UserID:   user.Id,
			Comment:  r.PostFormValue("comment"),
		})
	}); err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("%v", err)
		return
	}

	http.Redirect(w, r, "/review?id="+url.QueryEscape(strconv.Itoa(reviewId)), http.StatusFound)
}

func (s *server) createReview(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		s.templates.ExecuteTemplate(w, "create_review.html", nil)
		return
	}

	user, ok := r.Context().Value("user").(User)
	if !ok {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		log.Println("Failed type assertion")
		return
	}

	if err := r.ParseForm(); err != nil {
		http.Error(w, "Invalid form", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	rating, err := strconv.Atoi(r.PostFormValue("rating"))
	if err != nil {
		http.Error(w, "Invalid rating", http.StatusBadRequest)
		log.Printf("%v", err)
		return
	}

	isDraftInt := int64(0)
	if r.PostFormValue("is_draft") != "" {
		isDraftInt = 1
	}

	if err := s.withTx(r.Context(), func(queries *db.Queries) error {
		return queries.CreateReview(r.Context(), db.CreateReviewParams{
			UserID:      user.Id,
			ReviewTitle: r.PostFormValue("title"),
			BookTitle:   r.PostFormValue("book_title"),
			Isbn:        r.PostFormValue("isbn"),
			Rating:      int64(rating),
			Review:      r.PostFormValue("review"),
			IsDraft:     isDraftInt,
		})
	}); err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("%v", err)
		return
	}

	http.Redirect(w, r, "/", http.StatusFound)
}

var (
	firstNames []string
	lastNames  []string
)

func loadNameFile(path string) ([]string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	names := []string{}
	for _, line := range bytes.Split(data, []byte("\n")) {
		lineS := string(line)
		if lineS == "" {
			continue
		}
		s := strings.ToLower(lineS)
		names = append(names, strings.ToUpper(s[0:1])+s[1:])
	}

	return names, nil
}

func loadNames() error {
	maleNames, err := loadNameFile("names/malenames-usa-top1000.txt")
	if err != nil {
		return err
	}
	femaleNames, err := loadNameFile("names/femalenames-usa-top1000.txt")
	if err != nil {
		return err
	}
	firstNames = append(maleNames, femaleNames...)

	lastNames, err = loadNameFile("names/familynames-usa-top1000.txt")
	return err
}

func randomName() string {
	firstName := firstNames[rand.Int()%len(firstNames)]
	lastName := lastNames[rand.Int()%len(lastNames)]
	name := fmt.Sprintf("%s %s", firstName, lastName)
	return name
}

const SESSION_COOKIE = "session"

type User struct {
	Id       string
	Username string
}

func (s *server) authMiddleware(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var id string
		var username string
		cookie, err := r.Cookie(SESSION_COOKIE)
		if err != nil {
			id = uuid.NewString()
			username = randomName()

			if err := s.withQueries(r.Context(), func(queries *db.Queries) error {
				return queries.CreateUser(r.Context(), db.CreateUserParams{
					ID:       id,
					Username: username,
				})
			}); err != nil {
				http.Error(w, "Database error", http.StatusInternalServerError)
				log.Printf("authMiddleware: queries.CreateUser: %v", err)
				return
			}

			http.SetCookie(w, &http.Cookie{Name: SESSION_COOKIE, Value: id, MaxAge: 3600 * 10})
		} else {
			id = cookie.Value

			err := s.withQueries(r.Context(), func(queries *db.Queries) error {
				var err error
				username, err = queries.GetUsername(r.Context(), id)
				return err
			})
			if err == sql.ErrNoRows {
				http.SetCookie(w, &http.Cookie{Name: SESSION_COOKIE, Value: "", MaxAge: -1})
				http.Redirect(w, r, "/", http.StatusFound)
				return
			}
			if err != nil {
				http.Error(w, "Database error", http.StatusInternalServerError)
				log.Printf("authMiddleware: queries.GetUsername: %v", err)
				return
			}
		}

		ctx := r.Context()
		newCtx := context.WithValue(ctx, "user", User{
			Id:       id,
			Username: username,
		})
		handler.ServeHTTP(w, r.WithContext(newCtx))
	})
}

// function that creates a new database
func createDatabase() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		return nil, err
	}

	if _, err := db.Exec(schemaSQL); err != nil {
		return nil, err
	}

	if _, err := db.Exec(initSQL); err != nil {
		return nil, err
	}

	return db, nil
}

func main() {
	if err := loadNames(); err != nil {
		panic(err)
	}

	db, err := createDatabase()
	if err != nil {
		panic(err)
	}

	server := server{templates: template.Must(template.ParseGlob("templates/*.html")), db: db}

	go func() {
		// rensa databasen periodiskt
		for {
			<-time.After(time.Hour)
			server.db.Close()
			newDB, err := createDatabase()
			if err != nil {
				panic(err)
			}
			server.db = newDB
		}
	}()

	log.Println(server.templates.DefinedTemplates())

	mux := http.NewServeMux()
	mux.HandleFunc("/", server.index)
	mux.HandleFunc("/create_review", server.createReview)
	mux.HandleFunc("/review", server.review)
	mux.HandleFunc("/comment", server.comment)

	const BIND = ":5555"
	log.Printf("Listening on %s", BIND)
	if err := http.ListenAndServe(BIND, server.authMiddleware(mux)); err != nil {
		panic(err)
	}
}
