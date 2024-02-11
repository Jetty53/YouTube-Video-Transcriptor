#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tkinter import *
from tkinter import ttk
from pytube import YouTube
from PIL import Image, ImageTk
import urllib.request
import threading
import moviepy.editor
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.utils import make_chunks
import string
from googletrans import Translator


# In[2]:


root = Tk()
root.title("Video to Audio to Text")
root.geometry('650x450')
root.resizable(False, False)


# In[3]:


# video_thumbnail_frame = Frame(root, highlightbackground="black", highlightthickness=.1)
video_thumbnail_frame = Frame(root, relief = SUNKEN, bd = 1, width = 325, height = 200)
video_information_frame = LabelFrame(root, text = "Video Information", width = 325, height = 200)
video_url_frame = Frame(root, height = "80")
video_audio_frame = Frame(root, background="#F5C2C1")


# In[4]:


video_thumbnail_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
video_information_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
video_url_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)
video_audio_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)


# In[5]:


video_thumbnail_image_label = Label(video_thumbnail_frame)
video_thumbnail_image_label.place(anchor = "center", relx = .5, rely = .5)


# In[6]:


video_title_label = Label(video_information_frame, text = "Video Title: ")
video_title_label.place(anchor = "w", relx = .01, rely = .12)
video_author_label = Label(video_information_frame, text = "Video By: ")
video_author_label.place(anchor = "w", relx = .01, rely = .30)
video_view_label = Label(video_information_frame, text = "Video View Count: ")
video_view_label.place(anchor = "w", relx = .01, rely = .45)
video_publish_label = Label(video_information_frame, text = "Video Publish Date: ")
video_publish_label.place(anchor = "w", relx = .01, rely = .60)
video_id_label = Label(video_information_frame, text = "Video ID: ")
video_id_label.place(anchor = "w", relx = .01, rely = .75)


# In[7]:


url_label = Label(video_url_frame, text = "Enter Video URL: ")
url_label.place(anchor="w", relx=.08, rely=.5)
urlInput = Entry(video_url_frame, borderwidth=15, relief = FLAT)
urlInput.place(anchor="c", relx=.5, rely=.5, width=300, height=25)
url_done_btn = Button(video_url_frame, text = "DONE", command = lambda:get_video_info(urlInput.get()))
url_done_btn.place(anchor="e", relx=.85, rely=.5)


# In[8]:


stop_thread = threading.Event()


# In[9]:


def get_video_info(link):
    
    global video_thumbnail_image_label
    global video_desc_label
    global img
    global video_download_ongoing_label
    global audio_text_download_ongoing_label
    global download_video_btn
    global convert_video_to_text_btn
    
    download_video_btn["state"] = ACTIVE
    convert_video_to_text_btn["state"] = ACTIVE
    
    video_download_ongoing_label.configure(text = "")
    audio_text_download_ongoing_label.configure(text = "")
    
    video = YouTube(link)
    
    thumbnail_url = video.thumbnail_url
    
    urllib.request.urlretrieve(thumbnail_url, "thumbnail.jpg")
    thumbnail_image = Image.open("thumbnail.jpg").resize((325, 200), Image.ANTIALIAS) 
    
    img = ImageTk.PhotoImage(thumbnail_image)
    video_thumbnail_image_label.configure(image = img)
    video_thumbnail_image_label.configure(image = img)
    os.remove("thumbnail.jpg")
    
    video_title = "Video Title: " + video.title + '\n'
    video_author = "Video By: " + video.author + '\n'
    video_view_count = "Video View Count: " + str(video.views) + '\n'
    video_publish_date = "Video Publish Date: " + str(video.publish_date) + '\n'
    video_id = "Video ID: " + video.video_id + '\n'
    
    if len(video_title) >= 53:
        video_title = video_title[:52] + "..."

    video_title_label.configure(text = video_title)
    video_author_label.configure(text = video_author)
    video_view_label.configure(text = video_view_count)
    video_publish_label.configure(text = video_publish_date)
    video_id_label.configure(text = video_id)
    
    stop_thread.clear()


# In[10]:


tab = ttk.Notebook(video_audio_frame)
# tab.place(anchor = 'nw', width = 600, height = 135)
tab.pack(fill = BOTH, expand = 1)


# In[11]:


video_frame = Frame(video_audio_frame, height = 135)
audio_text_frame = Frame(video_audio_frame)


# In[12]:


video_frame.pack()
audio_text_frame.pack()


# In[13]:


tab.add(video_frame, text = "Download Video Only")
tab.add(audio_text_frame, text = "Download Video and Text Convert")


# In[14]:


video_download_ongoing_label = Label(video_frame, text = "", relief = SUNKEN, bd = 1, width = 650, height = 1)
video_download_ongoing_label.place(anchor = "s", relx = 0.5, rely = 1)


# In[15]:


def start_thread_process(num):

    if num == 1:
        video_download_thread = threading.Thread(target = lambda:download_video(urlInput.get()))
        loading_text_thread = threading.Thread(target = lambda:loading_text(1))
        video_download_thread.start()
        loading_text_thread.start()
        
    elif num == 2:
        audio_text_donwload_thread = threading.Thread(target = lambda:convert_video_to_text(urlInput.get(), video_language_cb.current(), audio_slicing_constraint_cb.current()))
        loading_text_thread = threading.Thread(target = lambda:loading_text(2))
        audio_text_donwload_thread.start() 
        loading_text_thread.start()


# In[16]:


def download_video(link):
    global url_done_btn
    global download_video_btn
    global convert_video_to_text_btn
    
    url_done_btn["state"] = DISABLED
    download_video_btn["state"] = DISABLED
    convert_video_to_text_btn["state"] = DISABLED
    
    
    only_video_download_folder = "Downloaded Videoes"
    
    if not os.path.isdir(only_video_download_folder):
        os.mkdir(only_video_download_folder)
    
    video = YouTube(link)
    my_video = video.streams.get_highest_resolution()
    my_video.download(only_video_download_folder)
    
    stop_thread.set()
    
    url_done_btn["state"] = ACTIVE
    download_video_btn["state"] = ACTIVE
    convert_video_to_text_btn["state"] = ACTIVE
    
    video_download_ongoing_label.configure(text = "Your Video is Successfully Downloaded")


# In[17]:


def loading_text(num):
    global video_download_ongoing_label
    global audio_text_download_ongoing_label
    
    if num == 1:
        st = "Video Downloading has started...Please Wait---"
        while True:
            video_download_ongoing_label.configure(text = st + "/")
            video_download_ongoing_label.configure(text = st + "-")
            video_download_ongoing_label.configure(text = st + "\\")
            
            if stop_thread.is_set():
                break
                
    elif num == 2:
        st = "Video to Text Conversion ongoing...Please Wait---"
        while True:
            audio_text_download_ongoing_label.configure(text = st + "/")
            audio_text_download_ongoing_label.configure(text = st + "-")
            audio_text_download_ongoing_label.configure(text = st + "\\")
            
            if stop_thread.is_set():
                break          


# In[18]:


download_video_btn = Button(video_frame, text = "Download Only Video", command = lambda:start_thread_process(1), state = DISABLED)
download_video_btn.place(anchor = "center", relx = .5, rely = .5)


# In[19]:


choose_video_language_label = Label(audio_text_frame, text = "Choose Video Language: ")
choose_video_language_label.place(anchor = "nw", relx = .02, rely = .2)

video_language = StringVar()

video_language_cb = ttk.Combobox(audio_text_frame, width = 20, textvariable = video_language, state="readonly")
video_language_cb['values'] = (
    ' Bengali - India', 
    ' Bengali - Bangladesh',
    ' Hindi',
    ' English - India',
    ' English - America', 
    ' English - Britain'
)
video_language_cb.place(anchor = "w", relx = .05, rely = .5)
video_language_cb.current(1)


# In[20]:


choose_video_language_label = Label(audio_text_frame, text = "Choose Audio Slicing Technique: ")
choose_video_language_label.place(anchor = "nw", relx = .32, rely = .2)

audio_slicing = StringVar()

audio_slicing_constraint_cb = ttk.Combobox(audio_text_frame, width = 30, textvariable = audio_slicing, state="readonly")
audio_slicing_constraint_cb['values'] = (
    ' Silence based - 500ms (recommended)', 
    ' Silence based - 250ms',
    ' Silence based - 200ms',
    ' Silence based - 100ms',
    ' Silence based - 50ms', 
    ' Time based - 1.5 min',
    ' Time based - 1 min',
    ' Time based - 50 sec',
    ' Time based - 40sec',
    ' Time based - 20sec'
)
audio_slicing_constraint_cb.place(anchor = "center", relx = .5, rely = .5)
audio_slicing_constraint_cb.current(0)


# In[21]:


audio_text_download_ongoing_label = Label(audio_text_frame, text = "", relief = SUNKEN, bd = 1, width = 650, height = 1)
audio_text_download_ongoing_label.place(anchor = "s", relx = 0.5, rely = 1)


# In[22]:


convert_video_to_text_btn = Button(audio_text_frame, text = "Download Video\n And\n Convert to Text", command = lambda:start_thread_process(2), state = DISABLED)
convert_video_to_text_btn.place(anchor = "e", relx = .9, rely = .5)


# In[23]:


def convert_video_to_text(link, lang_index, chunk_index):
    
    global url_done_btn
    global download_video_btn
    global convert_video_to_text_btn
    
    url_done_btn["state"] = DISABLED
    download_video_btn["state"] = DISABLED
    convert_video_to_text_btn["state"] = DISABLED
    
    video = YouTube(link)
    
    folder_name = video.title.translate(str.maketrans('', '', string.punctuation))
    
    folder_name = folder_name[:50].strip()
    
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    
    my_video = video.streams.get_highest_resolution().download(folder_name)
    os.rename(my_video, os.path.join(folder_name, "video.mp4"))
    
    
    downloaded_video = moviepy.editor.VideoFileClip(os.path.join(folder_name, "video.mp4"))
   
    
    audio = downloaded_video.audio
    audio.write_audiofile(os.path.join(folder_name, "audio.wav"))
    
    whole_text_pronounce = get_large_audio_transcription(folder_name, os.path.join(folder_name, "audio.wav"), lang_index, chunk_index)
    
    if(lang_index == 2):
        string_divide = whole_text_pronounce.split("<---|---|--->")
        
        text_filename_1 = os.path.join(folder_name, "final(pronounce).txt")
    
        f1 = open(text_filename_1, "x", encoding="utf-8")
        f1 = open(text_filename_1, "r+", encoding="utf-8")
        f1.write(string_divide[0])
        f1.close()
        
        translated_hindi_text = hindi_translation(string_divide[1])
        
        text_filename_2 = os.path.join(folder_name, "final(hindi_translated).txt")
    
        f2 = open(text_filename_2, "x", encoding="utf-8")
        f2 = open(text_filename_2, "r+", encoding="utf-8")
        f2.write(translated_hindi_text)
        f2.close()
        
    else:
        
        text_filename = os.path.join(folder_name, "final(pronounce).txt")
    
        f = open(text_filename, "x", encoding="utf-8")
        f = open(text_filename, "r+", encoding="utf-8")
        f.write(whole_text_pronounce)
        f.close()
    
     
    
    stop_thread.set()
    
    url_done_btn["state"] = ACTIVE
    download_video_btn["state"] = ACTIVE
    convert_video_to_text_btn["state"] = ACTIVE
    
    audio_text_download_ongoing_label.configure(text = "Your Video-Audio is Successfully Converted to Text")


# In[24]:


def get_large_audio_transcription(parent_folder, audio_path, lang_index, chunk_index):
    
    rec = sr.Recognizer()
    sound = AudioSegment.from_wav(audio_path)
    
    if(chunk_index == 0):
        chunks = split_on_silence(sound, min_silence_len = 500, silence_thresh = sound.dBFS-14, keep_silence = 500)
    elif(chunk_index == 1):
        chunks = split_on_silence(sound, min_silence_len = 250, silence_thresh = sound.dBFS-14, keep_silence = 500)
    elif(chunk_index == 2):
        chunks = split_on_silence(sound, min_silence_len = 200, silence_thresh = sound.dBFS-14, keep_silence = 500)
    elif(chunk_index == 3):
        chunks = split_on_silence(sound, min_silence_len = 100, silence_thresh = sound.dBFS-14, keep_silence = 500)
    elif(chunk_index == 4):
        chunks = split_on_silence(sound, min_silence_len = 50, silence_thresh = sound.dBFS-14, keep_silence = 500)
    elif(chunk_index == 5):
        chunks = make_chunks(sound, 90000)
    elif(chunk_index == 6):
        chunks = make_chunks(sound, 60000)
    elif(chunk_index == 6):
        chunks = make_chunks(sound, 50000)
    elif(chunk_index == 7):
        chunks = make_chunks(sound, 40000)
    else:
        chunks = make_chunks(sound, 20000)
    
    folder_name = "audio_chunks"
    folder_path = os.path.join(parent_folder, folder_name)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    whole_text = ""
    whole_hindi_text = ""
    for i, audio_chunk in enumerate(chunks, start = 1):
        chunk_filename = os.path.join(folder_path, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = rec.record(source)
            
            try:
                if(lang_index == 0):
                    text = rec.recognize_google(audio_listened, language = "bn-IN")
                elif(lang_index == 1):
                    text = rec.recognize_google(audio_listened, language = "bn-BD")
                elif(lang_index == 2):
                    text = rec.recognize_google(audio_listened, language = "en-IN")
                    text_trans = rec.recognize_google(audio_listened, language = "hi-IN")
                elif(lang_index == 3):
                    text = rec.recognize_google(audio_listened, language = "en-IN")
                elif(lang_index == 4):
                    text = rec.recognize_google(audio_listened, language = "en-US")
                else:
                    text = rec.recognize_google(audio_listened, language = "en-GB")
                
            except sr.UnknownValueError as e:
                print("Error: str(e)")
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text + '\n\n'
                if(lang_index == 2):
                    whole_hindi_text += text_trans + '\n\n'
                        
    if(lang_index == 2):
        final_text = whole_text + '\n\n<---|---|--->\n\n' + whole_hindi_text
        return final_text
    
    # return the text for all chunks detected
    return whole_text


# In[25]:


def hindi_translation(hindi_text_whole):
    translated_hindi_to_eng_whole = ""
    hindi_text_whole_divided_list = hindi_text_whole.split("\n\n")
    
    for i in range(len(hindi_text_whole_divided_list)):
        
        translator = Translator(service_urls=['translate.googleapis.com'])
        print(hindi_text_whole_divided_list[i])
        trans = translator.translate(hindi_text_whole_divided_list[i], dest='en')
        translated_hindi_to_eng_whole += trans.text + '\n\n'
    
    return translated_hindi_to_eng_whole


# In[26]:


root.mainloop()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




