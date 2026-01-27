import "./style.css";

type UploadResponse = {
  doc_id: string;
  object_key: string;
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
      <div class="eyebrow">PDFアップロード</div>
      <h1>プリントを取り込み</h1>
      <p class="lead">
        PDFをアップロードすると、内容の抽出処理に進みます。
        スキャンPDFの場合も後続でOCRにフォールバックします。
      </p>
      <form id="upload-form" class="form">
        <label class="file-input">
          <input id="file" type="file" accept="application/pdf" required />
          <span id="file-label">PDFを選択</span>
        </label>
        <button id="submit" type="submit">アップロード</button>
      </form>
      <div id="status" class="status" aria-live="polite"></div>
    </section>
    <section class="note">
      <h2>次のステップ</h2>
      <ul>
        <li>アップロード後にドキュメントIDが発行されます。</li>
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

  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("PDFを選択してください。", "error");
    return;
  }

  submitButton.disabled = true;
  setStatus("アップロード中...", "info");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/v1/uploads", {
      method: "PUT",
      body: formData,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || "アップロードに失敗しました。");
    }

    const data = (await response.json()) as UploadResponse;
    setStatus(`完了: doc_id=${data.doc_id}`, "success");
    fileInput.value = "";
  } catch (error) {
    const message = error instanceof Error ? error.message : "予期せぬエラーです。";
    setStatus(message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (!file) {
    fileLabel.textContent = "PDFを選択";
    setStatus("", "info");
    return;
  }
  fileLabel.textContent = file.name;
  setStatus(`選択中: ${file.name}`, "info");
});
