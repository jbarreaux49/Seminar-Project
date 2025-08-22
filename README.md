
# vision_app

To run the project, you must first connect a webcam to your computer and place it on a stand or in a fixed position where you are sure it will not move when you adjust the projector during calibration.

Once this is done, launch the program with the command:

```bash
python -m vision_app.app
```
Move the sliders to detect the blue border of the TV. Once this is done, press Next. You will then enter the second menu. At this point, you can turn on the projector and manually display the MainImage in full screen on it.

Make sure not to move the camera afterward, since the borders detected in the previous step are static and will not adapt if the camera is moved.

Align the projector as indicated by the program until you get the correct alignment. After that, close the program.

# Unity projection

After the calibration step, you can display your Unity project through this command:

```bash
python unity_projection.py --tv path/to/tv_image.jpg --obs path/to/obs_image.jpg

```


# Video Projection 

```bash
python video_projection.py
```