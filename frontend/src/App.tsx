import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { LANGS, translate, type Lang } from "./i18n";
import { getLang, getPending, setLang, setPending, submitTextSync } from "./sync";
import Home from "./pages/Home";
import Report from "./pages/Report";
import Track from "./pages/Track";
import Verify from "./pages/Verify";
import MissedCall from "./pages/MissedCall";

interface LangCtx {
  lang: Lang;
  set: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  online: boolean;
  pending: number;
  refreshPending: () => void;
}

const Ctx = createContext<LangCtx>(null!);
export const useApp = () => useContext(Ctx);

function Shell() {
  const [lang, setLangState] = useState<Lang>((getLang() as Lang) || "mr");
  const [online, setOnline] = useState(navigator.onLine);
  const [pending, setPendingCount] = useState(getPending().length);

  const refreshPending = useCallback(() => setPendingCount(getPending().length), []);

  const set = useCallback((l: Lang) => {
    setLangState(l);
    setLang(l);
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => translate(lang, key, vars),
    [lang]
  );

  // Flush the offline queue whenever connectivity returns.
  const flush = useCallback(async () => {
    const queue = getPending();
    if (!queue.length) return;
    setPendingCount(queue.length);
    const rest = await submitTextSync(queue);
    setPending(rest);
    setPendingCount(rest.length);
  }, []);

  useEffect(() => {
    const on = () => {
      setOnline(true);
      flush();
    };
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    flush();
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, [flush]);

  return (
    <Ctx.Provider value={{ lang, set, t, online, pending, refreshPending }}>
      <header>
        <Link className="logo" to="/">
          <img src={`${import.meta.env.BASE_URL}icons/icon.svg`} alt="" />
          <span>
            <b>JanSetu जनसेतु</b>
            <small>{t("tagline")}</small>
          </span>
        </Link>
        <div className="langswitch" role="group" aria-label="Language">
          {LANGS.map((l) => (
            <button
              key={l.code}
              className={lang === l.code ? "on" : ""}
              onClick={() => set(l.code)}
            >
              {l.label}
            </button>
          ))}
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report" element={<Report />} />
          <Route path="/track" element={<Track />} />
          <Route path="/verify" element={<Verify />} />
          <Route path="/missed-call" element={<MissedCall />} />
        </Routes>
      </main>
      <footer>
        JanSetu — public investment intelligence ·{" "}
        <a href="/docs" target="_blank" rel="noreferrer">
          API
        </a>{" "}
        ·{" "}
        <Link to="/">{t("back")}</Link>
      </footer>
    </Ctx.Provider>
  );
}

export default function App() {
  return (
    <BrowserRouter basename="/app">
      <Shell />
    </BrowserRouter>
  );
}
