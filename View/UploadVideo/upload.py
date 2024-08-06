from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import MDFileManager
from apputils import load_kv
import os
import shutil
from kivymd.toast import toast
from moviepy.editor import VideoFileClip
import cv2
from kivy.storage.jsonstore import JsonStore

# import markdown
# from docx import Document
# from docx.shared import Pt
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

#importing and configuring gemini api and modal
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API"))
modal = genai.GenerativeModel("gemini-1.5-flash")

load_kv(__name__)

class UploadScreen(MDScreen):
    # transition_state = "out"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, 
            select_path=self.select_path,
            # preview=True,
            ext=['.mp4']
        )
        # Defining global variables in local storage
        self.store = JsonStore("data.json")
        
    
    def file_manager_open(self):
        self.file_manager.show_disks()  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''
        self.exit_manager()
        # self.extractAudio(path)
        self.store.put("video_path", path=path)
        

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    
    def extractAudio(self):
        
        video_path = self.store.get("video_path")["path"]
        clip = VideoFileClip(video_path)
        audio_path = 'audio.mp3'
        clip.audio.write_audiofile(audio_path) # type: ignore
        clip.close()
        # toast(self.video_path)
        toast("audio extracted")

    def transcribe(self):
        
        audio_file = genai.upload_file(path="audio.mp3")
        
        # List all uploaded files.
        for file in genai.list_files():
            toast(f"{file.display_name}, URI: {file.uri}")

        promt = "read the speech"
        response = modal.generate_content([promt, audio_file])
        self.store.put("audio_text", text=response.text)
        
        toast(response.text)
        
        self.deleteFile(audio_file.name)    

    def get_files_in_folder(self, folder_path):
        files = []
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                files.append(filename)
        return files    
    
    def generateImageCaption(self):
        folderPath = "extracted_frames"
        filesInFoder = self.get_files_in_folder(folderPath)
        videoText = ""
        for file in filesInFoder:
            imagePath = os.path.join(folderPath, file)
            image_file = genai.upload_file(path=imagePath)
            getImage = genai.get_file(name=image_file.name)
            print(f"Retrieved file '{getImage.display_name}' as: {image_file.uri}")
            promt = "describe image in short"
            response = modal.generate_content([promt, image_file])
            videoText += response.text+" "
            self.deleteFile(image_file.name)
        
        self.store.put("video_text", text=videoText)
        toast(videoText)

    def deleteFile(self, file):
        #deleting file
        genai.delete_file(file)
        print("file deleted")

    def extractFrames(self):
        # Open the video file
        video_path = self.store.get("video_path")["path"]
        print(video_path)
        # return
        output_folder="extracted_frames/"
        interval_seconds=10

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        # Get video frame rate
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * interval_seconds)

        # Delete old folder
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        frame_count = 0
        saved_frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval_frames == 0:
                # Save frame as PNG file (or JPEG, adjust as needed)
                frame_path = os.path.join(output_folder, f"frame_{saved_frame_count:04d}.png")
                cv2.imwrite(frame_path, frame)
                saved_frame_count += 1

            frame_count += 1

        cap.release()
        toast(f"Extracted {saved_frame_count} frames")

    
    # functions for generating captions and sending to result screen
    def generateCaption(self):
        audio_text = self.store.get("audio_text")["text"]
        video_text = self.store.get("video_text")["text"]
        # final_result = self.store.get("final_result")["text"]
        # html_content = markdown.markdown(final_result)
        # document = Document()

        # # Parse HTML content and add to DOCX
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(html_content, 'html.parser')

        # for element in soup.descendants:
        #     if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        #         level = int(element.name[1])
        #         paragraph = document.add_heading(level=level)
        #         run = paragraph.add_run(element.get_text())
        #         run.font.size = Pt(12 + (6 - level) * 2)
        #     elif element.name == 'p':
        #         paragraph = document.add_paragraph()
        #         paragraph.add_run(element.get_text())
        #     elif element.name == 'ul':
        #         for li in element.find_all('li'):
        #             paragraph = document.add_paragraph(style='List Bullet')
        #             paragraph.add_run(li.get_text())
        #     elif element.name == 'ol':
        #         for li in element.find_all('li'):
        #             paragraph = document.add_paragraph(style='List Number')
        #             paragraph.add_run(li.get_text())
        #     elif element.name == 'strong':
        #         paragraph = document.add_paragraph()
        #         run = paragraph.add_run(element.get_text())
        #         run.bold = True
        #     elif element.name == 'em':
        #         paragraph = document.add_paragraph()
        #         run = paragraph.add_run(element.get_text())
        #         run.italic = True
        
        
        # document.save("output.docx")

        # print(content)
        # return
        response = modal.generate_content(f"""
                    Audio contains following information :\n
                    "{audio_text}"\n\n
                    And Video contains following information:
                    {video_text}\n
                    ---------------\n
                    According to both scenario create youtube title, description, hashtags and keywords.
                    """)
        
        # self.store.put("final_result", text=response.text)
        
        self.manager.get_screen("two").ids.data.text = response.text
        self.manager.transition.direction = "left"
        self.manager.current = "two"
        
        
    
    