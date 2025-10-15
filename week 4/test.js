var $ = t => n => {
    var o = t[n];
    if (o)
        return o();
    throw new Error("Module not found in bundle: " + n)
}
    ;
import se from "https://cdn.jsdelivr.net/npm/highlight.js@11/+esm";
var T, m;
function Q({ startTime: t, endTime: n, callback: o }) {
    m = {
        startTime: t,
        endTime: n,
        callback: o
    },
        requestAnimationFrame(C)
}
function C(t) {
    if (T !== void 0 && t - T < 1e3) {
        requestAnimationFrame(C);
        return
    }
    T = t;
    let n = new Date;
    n < m.startTime ? m.callback({
        status: "pending",
        time: m.startTime - n
    }) : n > m.endTime ? m.callback({
        status: "ended",
        time: n - m.endTime
    }) : m.callback({
        status: "running",
        time: m.endTime - n
    }),
        setTimeout(() => requestAnimationFrame(C), 1e3)
}
var I = t => {
    let n = Math.floor(t / 864e5)
        , o = Math.floor(t % 864e5 / 36e5)
        , r = Math.floor(t % 36e5 / 6e4)
        , i = Math.floor(t % 6e4 / 1e3)
        , l = u => String(u).padStart(2, "0");
    return n > 0 ? `${n}d ${l(o)}:${l(r)}:${l(i)}` : `${l(o)}:${l(r)}:${l(i)}`
}
    , w = t => {
        let n = {
            weekday: "short",
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "numeric",
            minute: "numeric",
            hour12: !0,
            timeZoneName: "short"
        };
        return t.toLocaleString("en-IN", n)
    }
    ;
function B(t) {
    let o = Math.round(t);
    if (Math.abs(t - o) < 1e-9)
        return String(o);
    let r = Math.round(t * 1e3) / 1e3;
    return String(r)
}
var te = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuYcxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMIDEkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXcWyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfWed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfISI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIXdQIDAQAB";
async function K(t) {
    let n = ne(te)
        , o = await crypto.subtle.importKey("spki", n, {
            name: "RSA-OAEP",
            hash: "SHA-256"
        }, !1, ["encrypt"])
        , r = new TextEncoder().encode(t)
        , i = await crypto.subtle.encrypt({
            name: "RSA-OAEP"
        }, o, r)
        , l = new Uint8Array(i);
    return btoa(String.fromCharCode(...l))
}
function ne(t) {
    let n = atob(t)
        , o = n.length
        , r = new Uint8Array(o);
    for (let i = 0; i < o; i++)
        r[i] = n.charCodeAt(i);
    return r.buffer
}
async function V(t) {
    let o = new TextEncoder().encode(t)
        , r = await crypto.subtle.digest("SHA-256", o);
    return Array.from(new Uint8Array(r)).map(u => u.toString(16).padStart(2, "0")).join("")
}
import { html as G, render as W } from "https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";
import ae from "https://cdn.jsdelivr.net/npm/jwt-decode@3/build/jwt-decode.esm.js";
function Y(t) {
    let n = JSON.parse(localStorage.getItem("user") || "null");
    return n ? W(G`
        <div id="logged-in-email" class="mb-3">You are logged in as <strong>${n.email}</strong>.</div>
        <div class="mb-3">
          <button
            class="btn btn-sm btn-outline-danger"
            @click=${() => {
            localStorage.removeItem("user"),
                location.reload()
        }
        }
          >
            Logout
          </button>
        </div>
      `, t) : (W(G`<div id="googleSignInButton" class="mx-auto" style="max-width: 200px"></div>`, t),
        google.accounts.id.initialize({
            client_id: "233761863432-t8g2u6esaeli8o2e2crvnu29u94ukt7k.apps.googleusercontent.com",
            callback: async o => {
                n = ae(o.credential);
                let r = await fetch(`/sign?id_token=${o.credential}`);
                if (!r.ok) {
                    alert(`Failed to sign you in: ${r.status}`);
                    return
                }
                n.quizSign = await r.text(),
                    localStorage.setItem("user", JSON.stringify(n)),
                    location.reload()
            }
        }),
        google.accounts.id.renderButton(document.getElementById("googleSignInButton"), {
            theme: "filled_black",
            size: "large",
            shape: "pill",
            logo_alignment: "left"
        })),
        n
}
var oe = $({
    "./exam-tds-2024-sep-roe1.info.js": () => import("./exam-tds-2024-sep-roe1.info.js"),
    "./exam-tds-2025-01-ga1.info.js": () => import("./exam-tds-2025-01-ga1.info.js"),
    "./exam-tds-2025-01-ga2.info.js": () => import("./exam-tds-2025-01-ga2.info.js"),
    "./exam-tds-2025-01-ga3.info.js": () => import("./exam-tds-2025-01-ga3.info.js"),
    "./exam-tds-2025-01-ga4.info.js": () => import("./exam-tds-2025-01-ga4.info.js"),
    "./exam-tds-2025-01-ga5.info.js": () => import("./exam-tds-2025-01-ga5.info.js"),
    "./exam-tds-2025-01-roe.info.js": () => import("./exam-tds-2025-01-roe.info.js"),
    "./exam-tds-2025-05-ga1.info.js": () => import("./exam-tds-2025-05-ga1.info.js"),
    "./exam-tds-2025-05-ga2.info.js": () => import("./exam-tds-2025-05-ga2.info.js"),
    "./exam-tds-2025-05-ga3.info.js": () => import("./exam-tds-2025-05-ga3.info.js"),
    "./exam-tds-2025-05-ga4.info.js": () => import("./exam-tds-2025-05-ga4.info.js"),
    "./exam-tds-2025-05-ga5.info.js": () => import("./exam-tds-2025-05-ga5.info.js"),
    "./exam-tds-2025-05-ga6.info.js": () => import("./exam-tds-2025-05-ga6.info.js"),
    "./exam-tds-2025-05-ga7.info.js": () => import("./exam-tds-2025-05-ga7.info.js"),
    "./exam-tds-2025-05-roe.info.js": () => import("./exam-tds-2025-05-roe.info.js"),
    "./exam-tds-2025-05-roe2.info.js": () => import("./exam-tds-2025-05-roe2.info.js"),
    "./exam-tds-2025-09-ga1.info.js": () => import("./exam-tds-2025-09-ga1.info.js"),
    "./exam-tds-2025-09-ga2.info.js": () => import("./exam-tds-2025-09-ga2.info.js"),
    "./exam-tds-2025-09-ga3.info.js": () => import("./exam-tds-2025-09-ga3.info.js"),
    "./exam-tds-2025-09-ga4.info.js": () => import("./exam-tds-2025-09-ga4.info.js"),
    "./exam-tds-project-virtual-ta.info.js": () => import("./exam-tds-project-virtual-ta.info.js"),
    "./exam-technical-assessment-2024-11.info.js": () => import("./exam-technical-assessment-2024-11.info.js")
});
var re = $({
    "./exam-tds-2024-sep-roe1.info.js": () => import("./exam-tds-2024-sep-roe1.info.js"),
    "./exam-tds-2024-sep-roe1.js": () => import("./exam-tds-2024-sep-roe1.js"),
    "./exam-tds-2025-01-ga1.info.js": () => import("./exam-tds-2025-01-ga1.info.js"),
    "./exam-tds-2025-01-ga1.js": () => import("./exam-tds-2025-01-ga1.js"),
    "./exam-tds-2025-01-ga2.info.js": () => import("./exam-tds-2025-01-ga2.info.js"),
    "./exam-tds-2025-01-ga2.js": () => import("./exam-tds-2025-01-ga2.js"),
    "./exam-tds-2025-01-ga3.info.js": () => import("./exam-tds-2025-01-ga3.info.js"),
    "./exam-tds-2025-01-ga3.js": () => import("./exam-tds-2025-01-ga3.js"),
    "./exam-tds-2025-01-ga4.info.js": () => import("./exam-tds-2025-01-ga4.info.js"),
    "./exam-tds-2025-01-ga4.js": () => import("./exam-tds-2025-01-ga4.js"),
    "./exam-tds-2025-01-ga5.info.js": () => import("./exam-tds-2025-01-ga5.info.js"),
    "./exam-tds-2025-01-ga5.js": () => import("./exam-tds-2025-01-ga5.js"),
    "./exam-tds-2025-01-roe.info.js": () => import("./exam-tds-2025-01-roe.info.js"),
    "./exam-tds-2025-01-roe.js": () => import("./exam-tds-2025-01-roe.js"),
    "./exam-tds-2025-05-ga1.info.js": () => import("./exam-tds-2025-05-ga1.info.js"),
    "./exam-tds-2025-05-ga1.js": () => import("./exam-tds-2025-05-ga1.js"),
    "./exam-tds-2025-05-ga2.info.js": () => import("./exam-tds-2025-05-ga2.info.js"),
    "./exam-tds-2025-05-ga2.js": () => import("./exam-tds-2025-05-ga2.js"),
    "./exam-tds-2025-05-ga3.info.js": () => import("./exam-tds-2025-05-ga3.info.js"),
    "./exam-tds-2025-05-ga3.js": () => import("./exam-tds-2025-05-ga3.js"),
    "./exam-tds-2025-05-ga4.info.js": () => import("./exam-tds-2025-05-ga4.info.js"),
    "./exam-tds-2025-05-ga4.js": () => import("./exam-tds-2025-05-ga4.js"),
    "./exam-tds-2025-05-ga5.info.js": () => import("./exam-tds-2025-05-ga5.info.js"),
    "./exam-tds-2025-05-ga5.js": () => import("./exam-tds-2025-05-ga5.js"),
    "./exam-tds-2025-05-ga6.info.js": () => import("./exam-tds-2025-05-ga6.info.js"),
    "./exam-tds-2025-05-ga6.js": () => import("./exam-tds-2025-05-ga6.js"),
    "./exam-tds-2025-05-ga7.info.js": () => import("./exam-tds-2025-05-ga7.info.js"),
    "./exam-tds-2025-05-ga7.js": () => import("./exam-tds-2025-05-ga7.js"),
    "./exam-tds-2025-05-roe.info.js": () => import("./exam-tds-2025-05-roe.info.js"),
    "./exam-tds-2025-05-roe.js": () => import("./exam-tds-2025-05-roe.js"),
    "./exam-tds-2025-05-roe2.info.js": () => import("./exam-tds-2025-05-roe2.info.js"),
    "./exam-tds-2025-05-roe2.js": () => import("./exam-tds-2025-05-roe2.js"),
    "./exam-tds-2025-09-ga1.info.js": () => import("./exam-tds-2025-09-ga1.info.js"),
    "./exam-tds-2025-09-ga1.js": () => import("./exam-tds-2025-09-ga1.js"),
    "./exam-tds-2025-09-ga2.info.js": () => import("./exam-tds-2025-09-ga2.info.js"),
    "./exam-tds-2025-09-ga2.js": () => import("./exam-tds-2025-09-ga2.js"),
    "./exam-tds-2025-09-ga3.info.js": () => import("./exam-tds-2025-09-ga3.info.js"),
    "./exam-tds-2025-09-ga3.js": () => import("./exam-tds-2025-09-ga3.js"),
    "./exam-tds-2025-09-ga4.info.js": () => import("./exam-tds-2025-09-ga4.info.js"),
    "./exam-tds-2025-09-ga4.js": () => import("./exam-tds-2025-09-ga4.js"),
    "./exam-tds-project-virtual-ta.info.js": () => import("./exam-tds-project-virtual-ta.info.js"),
    "./exam-tds-project-virtual-ta.js": () => import("./exam-tds-project-virtual-ta.js"),
    "./exam-technical-assessment-2024-11.info.js": () => import("./exam-technical-assessment-2024-11.info.js"),
    "./exam-technical-assessment-2024-11.js": () => import("./exam-technical-assessment-2024-11.js")
});
var R = document.body, q = document.getElementById("countdown"), O = document.getElementById("score"), ie = document.getElementById("login"), x = document.getElementById("notification"), ce = document.getElementById("instructions"), s = document.getElementById("exam-form"), M = document.getElementById("loading-questions"), H = document.getElementById("questions"), le = document.getElementById("sidebar-questions"), N = document.querySelectorAll(".check-action"), j = document.querySelectorAll(".save-action"), D = document.getElementById("submission-status"), de, F, p, A, E, z;
async function Te(t) {
    let n;
    try {
        n = await oe(`./exam-${t}.info.js`)
    } catch {
        s.innerHTML = `
      <div class="alert alert-danger" role="alert">
        <h4 class="alert-heading">Error!</h4>
        <p>Sorry, we couldn't find the quiz ${t}. You might have the wrong link.</p>
        <hr>
        <p class="mb-0">Please contact the exam team for assistance.</p>
      </div>`,
            s.classList.remove("d-none");
        return
    }
    let { title: o, start: r, end: i, admin: l, instructions: u, allowed: h, read: g } = n.default;
    document.title = o,
        ce.innerHTML = u;
    let c = Y(ie, {
        quiz: t
    });
    if (!c || !c.email)
        return;
    p = l ? l(c.email) : !1,
        navigator.sendBeacon("./log", JSON.stringify({
            quiz: t,
            email: c.email
        }));
    let v = new URLSearchParams(window.location.search);
    p && v.get("email") && (c.email = v.get("email"),
        document.title = `[As ${c.email}] ${document.title}`),
        A = p || (h ? h(c.email) : !0),
        E = !A && (g ? g(c.email) : !1);
    let f = new Date(typeof r == "function" ? r(c.email) : r)
        , b = new Date(typeof i == "function" ? i(c.email) : i);
    Q({
        startTime: f,
        endTime: b,
        callback: e
    }),
        f > new Date && !p ? (s.innerHTML = `<div class="alert alert-info" role="alert">
      <h4 class="alert-heading">Exam not yet started</h4>
      <p>The exam will start at ${w(f)}.</p>
    </div>`,
            s.classList.remove("d-none")) : A ? (await P(t, c),
                X(t, c)) : E ? (await P(t, c),
                    x.innerHTML = `<div class="alert alert-info" role="alert">
      <h4 class="alert-heading">Reading only</h4>
      <p>You can read the questions, but you cannot submit your own answers.</p>
    </div>`) : (s.innerHTML = `<div class="alert alert-danger" role="alert">
      <h4 class="alert-heading">Not authorized</h4>
      <p>${c.email} is not allowed to take this exam.</p>
      <p>Log in as an authorized user or contact the exam team for assistance.</p>
    </div>`,
            s.classList.remove("d-none")),
        x.addEventListener("click", a => {
            a.target.classList.contains("load-answers") && (Z(z[a.target.dataset.index].result.answers),
                a.target.textContent = "Loaded",
                a.target.classList.add("btn-success"),
                a.target.disabled = !0)
        }
        );
    function e({ status: a, time: d }) {
        R.dataset.status = p ? "admin" : a,
            a == "pending" ? q.textContent = d < 24 * 60 * 60 * 1e3 ? `Starts in ${I(d)}` : `Starts ${w(f)}` : a == "ended" ? q.textContent = `Ended at ${w(b)}` : a == "running" && (q.textContent = d < 24 * 60 * 60 * 1e3 ? `${I(d)} left` : `Due ${w(b)}`),
            F || P(t, c)
    }
}
var U = !1;
async function P(t, n) {
    if ((A || E) && !U) {
        let v = function () {
            h = Object.values(u).reduce((e, a) => e + a, 0),
                g = Object.values(i).reduce((e, a) => e + a.weight, 0),
                O.textContent = `Score: ${B(h)} / ${B(g)}`
        };
        U = !0;
        let o = window.location.hash.slice(1);
        M.classList.remove("d-none"),
            o && M.scrollIntoView({
                behavior: "smooth",
                block: "center"
            }),
            s.classList.remove("d-none");
        let r = new Map([[H, "questions"], [le, "index"]]);
        F = (await re(`./exam-${t}.js`)).questions;
        let i;
        try {
            i = await F(n, r)
        } catch (e) {
            H.innerHTML = `<div class="alert alert-danger" role="alert">
        <h4 class="alert-heading">Error!</h4>
        <p>Sorry, we couldn't load the questions. That's strange.</p>
        <pre>${e.message}

${e.stack}</pre>
        <hr>
        <p class="mb-0">Please contact the exam team for assistance.</p>
      </div>`;
            return
        }
        if (M.classList.add("d-none"),
            se.highlightAll(),
            o) {
            let e = document.getElementById(o);
            e && e.scrollIntoView({
                behavior: "smooth"
            })
        } else
            R.scrollIntoView();
        !p && (E || R.dataset.status != "running") && ([...N, ...j, O].forEach(e => e.disabled = !0),
            H.querySelectorAll("input, textarea, .card-footer button").forEach(e => e.disabled = !0)),
            s.querySelectorAll(".form-control").forEach(e => {
                e.parentNode.querySelector(".valid-feedback, .invalid-feedback") || e.insertAdjacentHTML("afterend", `<div class="valid-feedback mb-3 comment">Correct!</div>
            <div class="invalid-feedback mb-3 comment">Incorrect. Try again.</div>`)
            }
            ),
            [...N, ...j, O].forEach(e => e.classList.remove("d-none")),
            s.addEventListener("input", async () => {
                localStorage.setItem(`exam:${n.email}`, JSON.stringify(Object.fromEntries(new FormData(s))))
            }
            ),
            s.addEventListener("click", e => {
                e.target.closest(".check-answer") && f(e.target.dataset.question)
            }
            ),
            Z(JSON.parse(localStorage.getItem(`exam:${n.email}`) || "{}"));
        let l = e => {
            e.preventDefault(),
                c()
        }
            ;
        [...N].forEach(e => e.addEventListener("click", l)),
            [...j].forEach(e => e.addEventListener("click", b)),
            s.addEventListener("submit", l);
        let u = {}
            , h = 0
            , g = 0;
        async function c() {
            let e = Object.fromEntries(new FormData(s));
            document.querySelectorAll(".check-action").forEach(a => {
                a.disabled = !0,
                    a.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>'
            }
            );
            for (let a of Object.keys(e))
                s.querySelector(`[data-question="${a}"] .invalid-feedback`).textContent = "Checking...",
                    s.querySelector(`[data-question="${a}"] .valid-feedback`).textContent = "Checking...";
            for (let a of Object.keys(e))
                await f(a, e);
            return document.querySelectorAll(".check-action").forEach(a => {
                a.disabled = !1,
                    a.innerHTML = "Check all"
            }
            ),
            {
                answers: e,
                scores: u,
                total: h,
                max: g
            }
        }
        async function f(e, a = null) {
            let d = s.querySelector(`.check-answer[data-question="${e}"]`);
            d.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>',
                d.disabled = !0,
                a = a ?? Object.fromEntries(new FormData(s));
            let L = a[e]
                , S = s.querySelector(`[data-question="${e}"]`)
                , _ = s.querySelector(`[name="${e}"]`);
            S.querySelector(".invalid-feedback").textContent = "Checking...",
                S.querySelector(".valid-feedback").textContent = "Checking...";
            let k = i[e].answer ?? null
                , y = !1
                , J = "Incorrect. Try again.";
            if (typeof k == "function")
                try {
                    y = await k(L)
                    const checkResult = await k(L); // L is the submitted value already available in f
                    console.log(`i[${e}].answer() result:`, checkResult);
                } catch (ee) {
                    J = ee
                }
            else
                k === null ? L && (y = !0) : y = L === k.toString();
            return u[e] = y ? i[e].weight : 0,
                S.querySelector(".invalid-feedback").textContent = J,
                S.querySelector(".valid-feedback").textContent = "Correct",
                _.setCustomValidity(y ? "" : "Incorrect answer"),
                S.classList.add("was-validated"),
                d.innerHTML = "Check",
                d.disabled = !1,
                v(),
                y
        }
        async function b() {
            let e = await c();
            Object.assign(e, {
                quiz: t,
                deadline: de,
                email: n.email,
                quizSign: n.quizSign
            }),
                e.signature = await K(await V(JSON.stringify(e))),
                D.innerHTML = '<div class="spinner-border" role="status"></div>',
                D.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            let a;
            try {
                a = await fetch("./submit", {
                    method: "POST",
                    body: JSON.stringify(e)
                }).then(d => d.json())
            } catch (d) {
                a = {
                    error: d.message
                }
            }
            D.innerHTML = a.error ? `
          <div class="alert alert-danger" role="alert">
            <h4 class="alert-heading">Error!</h4>
            <p>${a.error}</p>
            <hr>
            <p class="mb-0">Please contact the exam team for assistance.</p>
          </div>` : `
          <div class="alert alert-success" role="alert">
            <h4 class="alert-heading">${a.data}</h4>
            <p class="mb-0">If you submit again, it will overwrite your previous submission and score.</p>
          </div>`,
                a.error || X(t, n)
        }
    }
}
var ue = (t, n) => `<div class="d-flex align-items-center mt-2">
  <button class="btn btn-sm btn-outline-primary me-2 load-answers" data-bs-toggle="collapse" data-index="${n}">Reload</button>
  from ${new Date(t.time).toLocaleString()}. Score: ${t.total}
</div>`;
async function X(t, n) {
    x.innerHTML = '<div class="spinner-border" role="status"></div>',
        await fetch(`./filter?quiz=${t}&email=${n.email}&history=1&limit=3`).then(o => o.json()).then(({ data: o }) => {
            x.innerHTML = `<div class="alert alert-success" role="alert">
        <h4 class="alert-heading">Recent saves <small class="text-muted fs-6 fw-light">(most recent is your official score)</small></h4>
        ${o.length ? o.map(ue).join("") : "<p>No recent saves</p>"}
        </div>`,
                z = o
        }
        )
}
function Z(t) {
    for (let [n, o] of Object.entries(t)) {
        let r = s.querySelector(`[name="${n}"]`);
        r && r.type != "file" && (r.value = o)
    }
}
export { Te as setup };
