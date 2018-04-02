#!/bin/bash

# Stitch all frames together in an MP4 file Note the FPS can be adjusted to match 16.5s duration.
ffmpeg -r 10 -f image2 -s 1920x1080 -i Frames/frame%d0.png -vcodec libx264 -crf 10 -pix_fmt yuv420p Animation.mp4

#Convert the .mp4 to gif
ffmpeg -i Animation.mp4 -crf 10 Animation.gif
