import "./style.css";

type UploadResponse = {
  doc_id: string;
  object_keys: string[];
  bucket: string;
};

const app = document.querySelector<HTMLDivElement>("#app");

const canonicalPath = "/uploads";
if (window.location.pathname === "/") {
  window.history.replaceState({}, "", canonicalPath);
}

if (!app) {
  throw new Error("appが見つかりません。");
}

app.innerHTML = `
  <main class="page">
    <section class="card">
      <div class="eyebrow">画像アップロード</div>
      <h1>プリント画像を取り込み</h1>
      <p class="lead">
        画像をアップロードすると、内容の抽出処理に進みます。
        PNG/JPEGに対応しています。
      </p>
      <form id="upload-form" class="form">
        <label class="file-input">
          <input id="file" type="file" accept="image/png,image/jpeg" multiple required />
          <span id="file-label">画像を選択</span>
        </label>
        <button id="submit" type="submit">アップロード</button>
      </form>
      <div id="status" class="status" aria-live="polite"></div>
    </section>
    <section class="note">
      <h2>次のステップ</h2>
      <ul>
        <li>アップロード後に取り込み処理が開始されます。</li>
        <li>取り込みジョブが完了すると質問回答が可能になります。</li>
      </ul>
    </section>
  </main>
`;

const form = document.querySelector<HTMLFormElement>("#upload-form");
const fileInput = document.querySelector<HTMLInputElement>("#file");
const status = document.querySelector<HTMLDivElement>("#status");
const submitButton = document.querySelector<HTMLButtonElement>("#submit");
const fileLabel = document.querySelector<HTMLSpanElement>("#file-label");

if (!form || !fileInput || !status || !submitButton || !fileLabel) {
  throw new Error("必要な要素が見つかりません。");
}

const setStatus = (message: string, tone: "info" | "error" | "success") => {
  status.textContent = message;
  status.dataset.tone = tone;
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

    const response = await fetch("/api/v1/uploads", {
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
