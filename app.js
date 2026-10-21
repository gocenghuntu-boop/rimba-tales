const $ = (id) => document.getElementById(id);
let currentStory = null;
let currentLang = "en";

function stopAllAudio() {
  const player = $("player");
  player.pause();
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  $("stopBtn").hidden = true;
}

$("makeStory").addEventListener("click", async () => {
  const btn = $("makeStory");
  btn.disabled = true;
  $("status").textContent = "Writing tonight's story…";
  stopAllAudio();
  try {
    const res = await fetch("/api/story", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        animal: $("animal").value,
        theme: $("theme").value,
        language: $("language").value,
        child_name: $("childName").value.trim(),
      }),
    });
    const data = await res.json();
    currentStory = data;
    currentLang = $("language").value;
    $("storyTitle").textContent = data.title;
    $("storySource").textContent = "Story source: " + data.source;
    $("storyText").innerHTML = data.text
      .split(/\n\s*\n/)
      .map((p) => `<p>${p.replace(/</g, "&lt;")}</p>`)
      .join("");
    $("storyCard").hidden = false;
    $("status").textContent = "";
    $("storyCard").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    $("status").textContent = "Something hiccuped. Try once more.";
  } finally {
    btn.disabled = false;
  }
});

$("listenBtn").addEventListener("click", async () => {
  if (!currentStory) return;
  const btn = $("listenBtn");
  btn.disabled = true;
  btn.textContent = "Preparing the voice…";
  stopAllAudio();
  try {
    const res = await fetch("/api/narrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: currentStory.text, language: currentLang }),
    });
    const data = await res.json();
    if (data.audio_base64) {
      const player = $("player");
      player.src = "data:" + (data.content_type || "audio/mpeg") + ";base64," + data.audio_base64;
      player.hidden = false;
      $("stopBtn").hidden = false;
      await player.play();
    } else {
      speakWithBrowser(currentStory.text, currentLang);
    }
  } catch (e) {
    speakWithBrowser(currentStory.text, currentLang);
  } finally {
    btn.disabled = false;
    btn.textContent = "🔊 Read it to us";
  }
});

function speakWithBrowser(text, lang) {
  if (!("speechSynthesis" in window)) {
    alert("Sorry, this device has no built-in voice to read with.");
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = lang === "id" ? "id-ID" : "en-US";
  utter.rate = 0.92;
  const voices = window.speechSynthesis.getVoices();
  const match = voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(utter.lang.slice(0, 2)));
  if (match) utter.voice = match;
  utter.onend = () => { $("stopBtn").hidden = true; };
  $("stopBtn").hidden = false;
  window.speechSynthesis.speak(utter);
}

$("stopBtn").addEventListener("click", stopAllAudio);
