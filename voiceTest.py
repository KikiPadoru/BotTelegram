from gtts import gTTS
text = 'как дела'
tts = gTTS(text=text, lang="ru")
tts.save('hello.mp3')
