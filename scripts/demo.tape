# Record with scripts/demo.sh
Output docs/images/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1100
Set Height 780
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 60ms
Set Framerate 10

Hide
Type "mkdir -p /demo && cp scripts/demo/movie.en.srt /demo/ && cd /demo && export PS1='$ ' && clear"
Enter
Show

Sleep 500ms
Type "cat movie.en.srt"
Enter
Sleep 5s

Type "cleanit -t default movie.en.srt"
Sleep 500ms
Enter
Sleep 3s

Type "cat movie.en.srt"
Enter
Sleep 7s
