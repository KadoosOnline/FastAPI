# Bruno — your API workbench for the whole course

[Bruno](https://www.usebruno.com) is a free, open-source app for sending HTTP
requests by hand: pick a method, type a URL, add headers or a JSON body, press
Send, read the status code and the response.

We use it in **every session**: first against a public API (today), then
against the Training Center API that we build ourselves. Each session's
project folder has a small `bruno/` collection like this one.

Why Bruno and not Postman? A Bruno collection is a folder of plain text
`.bru` files. It lives inside the project, goes into Git with the code, and
needs no account. (Postman works too, if you already know it.)

## Open this collection

1. Install Bruno from <https://www.usebruno.com/downloads>.
2. **Open Collection** → choose this folder (`13_bruno_first_requests`).
3. Top right: select the environment **public**.
4. Open `List posts of user 1` and press **Ctrl+Enter**.

## What is inside

| File | What it shows |
|------|---------------|
| `01-list-posts.bru` | `GET` with a query parameter (`?userId=1`) |
| `02-get-post.bru` | `GET` one resource by id |
| `03-create-post.bru` | `POST` with a JSON body and a header → `201 Created` |
| `04-not-found.bru` | a `404` — errors are normal answers, read them |

Every request has a **Tests** tab with a small check, e.g.
`expect(res.status).to.equal(200)`. Run the whole folder with the
**Runner** and see all green.

## Variables

`{{publicApi}}` is an **environment variable** (see `environments/public.bru`).
Change the server once, and every request follows. Later we will store the
login token in a variable too.
