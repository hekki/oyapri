import { marked } from "marked";
import "./style.css";

type UploadResponse = {
  doc_id: string;
  object_keys: string[];
  bucket: string;
};

type SearchResult = {
  doc_id: number;
  page_start: number | null;
  page_end: number | null;
  content: string;
  distance: number;
};

type SearchResponse = {
  query: string;
  results: SearchResult[];
};

type AskCitation = {
  doc_id: number;
  page_start: number | null;
  page_end: number | null;
  quote: string;
};

type AskResponse = {
  answer: string;
  citations: AskCitation[];
};

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("appが見つかりません。");
}

app.innerHTML = `
  <main class="page">
    <header class="hero">
      <div class="eyebrow">OYAPRI</div>
      <h1 class="hero-title">プリント検索アシスタント</h1>
      <p class="hero-sub">画像を取り込み、内容を日本語で質問できます。</p>
    </header>
    <section class="card">
      <div class="eyebrow">質問</div>
      <h2>内容について質問</h2>
      <form id="search-form" class="form">
        <label class="text-input">
          <textarea id="query" placeholder="例: 1月のイベントを教えて" required></textarea>
        </label>
        <button id="search-submit" type="submit">質問</button>
      </form>
      <div id="search-status" class="status" aria-live="polite"></div>
      <div id="search-results" class="results"></div>
    </section>
    <section class="card">
      <div class="eyebrow">画像アップロード</div>
      <h2>プリント画像を取り込み</h2>
      <p class="lead">
        画像をアップロードすると、内容の抽出処理に進みます。
        PNG/JPEGに対応しています。
      </p>
      <ul class="steps">
        <li>アップロード後に取り込み処理が開始されます。</li>
        <li>取り込み完了後に質問への回答ができます。</li>
      </ul>
      <form id="upload-form" class="form">
        <label class="file-input">
          <input id="file" type="file" accept="image/png,image/jpeg" multiple required />
          <span id="file-label">画像を選択</span>
        </label>
        <button id="submit" type="submit">アップロード</button>
      </form>
      <div id="status" class="status" aria-live="polite"></div>
    </section>
  </main>
`;

const form = document.querySelector<HTMLFormElement>("#upload-form");
const fileInput = document.querySelector<HTMLInputElement>("#file");
const status = document.querySelector<HTMLDivElement>("#status");
const submitButton = document.querySelector<HTMLButtonElement>("#submit");
const fileLabel = document.querySelector<HTMLSpanElement>("#file-label");
const searchForm = document.querySelector<HTMLFormElement>("#search-form");
const queryInput = document.querySelector<HTMLTextAreaElement>("#query");
const searchStatus = document.querySelector<HTMLDivElement>("#search-status");
const searchResults = document.querySelector<HTMLDivElement>("#search-results");
const searchButton = document.querySelector<HTMLButtonElement>("#search-submit");

if (
  !form ||
  !fileInput ||
  !status ||
  !submitButton ||
  !fileLabel ||
  !searchForm ||
  !queryInput ||
  !searchStatus ||
  !searchResults ||
  !searchButton
) {
  throw new Error("必要な要素が見つかりません。");
}

const setStatus = (message: string, tone: "info" | "error" | "success") => {
  status.textContent = message;
  status.dataset.tone = tone;
};

const setSearchStatus = (message: string, tone: "info" | "error" | "success") => {
  searchStatus.textContent = message;
  searchStatus.dataset.tone = tone;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const files = fileInput.files;
  if (!files || files.length === 0) {
    setStatus("画像を選択してください。", "error");
    return;
  }

  submitButton.disabled = true;
  setStatus("アップロード中...", "info");

  try {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch("/api/v1/", {
      method: "PUT",
      body: formData,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || "アップロードに失敗しました。");
    }

    await response.json();
    setStatus("アップロード完了。取り込みを開始します。", "success");
    fileInput.value = "";
  } catch (error) {
    const message = error instanceof Error ? error.message : "予期せぬエラーです。";
    setStatus(message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  if (!query) {
    setSearchStatus("検索クエリを入力してください。", "error");
    return;
  }

  searchButton.disabled = true;
  setSearchStatus("検索中...", "info");
  searchResults.innerHTML = "";

  try {
    const response = await fetch("/api/v1/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: query, top_k: 5}),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || "検索に失敗しました。");
    }

    const data = (await response.json()) as AskResponse;
    if (!data.answer) {
      setSearchStatus("該当する結果がありません。", "info");
      return;
    }
    setSearchStatus("回答:", "success");
    const rendered = marked.parse(data.answer);
    searchResults.innerHTML = `
      <article class="result">
        <div class="quote">${rendered}</div>
      </article>
    `;
  } catch (error) {
    const message = error instanceof Error ? error.message : "予期せぬエラーです。";
    setSearchStatus(message, "error");
  } finally {
    searchButton.disabled = false;
  }
});

queryInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") {
    return;
  }
  if ((event as KeyboardEvent).isComposing) {
    return;
  }
  if (event.shiftKey) {
    return;
  }
  event.preventDefault();
  searchForm.requestSubmit();
});

fileInput.addEventListener("change", () => {
  const files = fileInput.files;
  if (!files || files.length === 0) {
    fileLabel.textContent = "画像を選択";
    setStatus("", "info");
    return;
  }
  const names = Array.from(files)
    .map((file) => file.name)
    .join(", ");
  fileLabel.textContent = `${files.length}件選択`;
  setStatus(`選択中: ${names}`, "info");
});
