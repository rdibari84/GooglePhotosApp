### GooglePhotosApp
Command line utilty to create albumbs and bulk upload images

#### To Run
1. Source venv or create one & then source
  ```
  source venv/bin/activate
  ```
OR
  ```
  virtualenv -p python3 venv 
  source venv/bin/activate
  ```

2. Install dependencies 
  ```
  pip install -r requirements.txt
  ```

3. Run
To list albums
  ```
  python main.py --action list_albums
  ```
To upload
  ```
  python main.py --action upload --filename /usr/local/tmp/filename.png --albumid 1iy3bcue8f3b
  ```
To create album
  ```
  python main.py --action create_album --name TheBestTime
  ````
