# Cloudflare Worker — fpi-demo.alvintola.com

A small reverse proxy in front of the FPI sample dashboard on Streamlit
Community Cloud.

## Why it exists

Streamlit Community Cloud routes requests by the `Host` header. A plain CNAME
from `fpi-demo.alvintola.com` to `*.streamlit.app` returns a 404. This Worker
fetches the app at its real hostname and returns the response on the custom
domain. It also:

- rewrites `Origin` / `Referer` so Streamlit's XSRF check passes
- preserves the `Upgrade: websocket` response so `/_stcore/stream` works
- rewrites same-origin `Location` headers back to the custom domain
- redirects `/` to the raw app path `/~/+/`, avoiding Streamlit's viewer shell

## Setup order

1. Push this repo to GitHub.
2. In Streamlit Community Cloud, create an app from the repo:
   - main file: `app.py`
   - Python: 3.13
3. Copy the resulting app URL (for example
   `https://fpi-marketing-dashboard.streamlit.app`).
4. Set `APP_ORIGIN` in `wrangler.jsonc` to that URL.
5. Deploy:

```bash
cd cloudflare-worker
npx --yes wrangler@latest deploy
```

Requires a Wrangler login that can edit the `alvintola.com` zone.

Until `APP_ORIGIN` is set, the Worker returns a 503 with a setup message.

## Note

The app is an independent portfolio sample. All data is synthetic and it is not
affiliated with, commissioned by, or endorsed by Freedom Property Investors.
