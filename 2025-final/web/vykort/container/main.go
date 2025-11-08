package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"os"

	"github.com/hoisie/mustache"
)

//go:embed static/*
var efs embed.FS

func main() {
	err := realMain()
	if err != nil {
		fmt.Println(err.Error())
		os.Exit(0)
	}
}

func realMain() error {

	mux := http.NewServeMux()

	efs, err := fs.Sub(efs, "static")
	if err != nil {
		return err
	}

	mux.Handle("GET /", http.FileServerFS(efs))

	mux.HandleFunc("POST /vykort", func(w http.ResponseWriter, r *http.Request) {

		type reqS struct {
			Template string            `json:"template"`
			Data     map[string]string `json:"data"`
		}
		var req reqS

		err = json.NewDecoder(r.Body).Decode(&req)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			return
		}

		t, err := mustache.ParseString(req.Template)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("github.com/hoisie/mustache: " + err.Error()))
			return
		}

		w.Write([]byte(t.Render(req.Data)))

	})

	http.ListenAndServe("0.0.0.0:8000", mux)

	return nil
}
