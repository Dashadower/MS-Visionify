## CNN to solve runes automatically
This directory contains the necessary files to generate images and train a CNN from the images.

Info on scripts on this dir:
* convert_img2gray.py: Converts Images in given directory to grayscale using coversion method listed below
* count_images.py: returns a count of files in given directories
* keras_model_verifier.py: simple script to test trained model against running maplestory
* merge_images.py: when you have 2 directories containing a subdir of categories, merges images using labeldata.txt
* move_traindata2test.py: moves some images of each class folder to a different directory class folder
* rune_dataset_classifier: tool to classify directory of 60x60 images into classes.
* rune_screen_cacpture.py: tool to capture maplestory screen in rgb
* train_keras.py: CNN train script

### How to use it:
1. Create subdirectory `images` and underlying directories. Result should be:
    ```
    images/
        cropped/
            traindata/
            testdata/
        screenshots/
   ```
   
2. Run `rune_screen_capture.py` while you have MS open. Now find runes and after activating them, press `s` or `d` to take screenshots of the rune ROI
3. Run `rune_dataset_classifier.py`. After you have a sufficient amount of uncropped images, this script will process them, find the indivisual rune arrows within the images.
    You have to manually classify them using your arrow keys. Once it's done, it will generate images into `traindata`.
4. Run `move_traindata2testpy` This script will move an equal amount of images from `cropped/traindata` to `cropped/testdata`. 80 to 20
    is a good amount
5. Run `trainer_keras.py`. This will start the training.

## *Note on dataset*

I did not include the dataset I have personally used, to prevent malicious users getting stuff without effort. ~~If you would like
to request the dataset, please personally contact me.~~ Under no circumstances I will release any more information related
to botting or the repo itself.