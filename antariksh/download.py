from pytube import YouTube

yt= YouTube('https://www.youtube.com/watch?v=t0Q2otsqC4I')
stream = yt.streams.filter(only_audio=True)
itag = None
abr = 0
for i in stream:
    if int(i.abr.replace('kbps', ''))>abr:
        itag = i.itag
        abr = int(i.abr.replace('kbps', ''))
stream = yt.streams.get_by_itag(itag)
stream.download(output_path='/tmp/newsong.mp3')