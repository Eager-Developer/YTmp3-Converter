from datetime import datetime
import os
import re
import traceback
import yt_dlp

#region Constants and global variables

print("--- PLEASE NOTICE - Default value is picked if you press the enter key without typing anything ---\n")

COMMON_WIN_DRIVES = ['C', 'D', 'S', 'E']
default_win_drive = None
for COMMON_WIN_DRIVE in reversed(COMMON_WIN_DRIVES):
    if os.path.exists(COMMON_WIN_DRIVE + ":\\" + "Downloads\\"):
        default_win_drive = COMMON_WIN_DRIVE
DEFAULT_WIN_DRIVE = default_win_drive + ":\\"

DEFAULT_OUTPUT_FOLDER_NAME = "MP3 conversion result"
output_folder_name = input("Output folder name [DEFAULT = \"" + DEFAULT_OUTPUT_FOLDER_NAME + "\"]: ").strip()
if not(output_folder_name):
    output_folder_name = DEFAULT_OUTPUT_FOLDER_NAME
OUTPUT_FOLDER_NAME = output_folder_name + "\\"

if (not(DEFAULT_WIN_DRIVE)):
    output_base_dir_path = input("Output folder path (i.e. \"C:\\Downloads\\\"): ").strip()
else:
    DEFAULT_OUTPUT_BASE_DIR_PATH = "./"#DEFAULT_WIN_DRIVE + "Downloads\\YTmp3\\"
    output_base_dir_path = input("Output folder path [DEFAULT = \"" + DEFAULT_OUTPUT_BASE_DIR_PATH + "\"]: ").strip()
    if not(output_base_dir_path):
        output_base_dir_path = DEFAULT_OUTPUT_BASE_DIR_PATH
OUTPUT_BASE_DIR_PATH = output_base_dir_path

OUTPUT_FOLDER_PATH = OUTPUT_BASE_DIR_PATH + OUTPUT_FOLDER_NAME

DEFAULT_LINKS_FILE_NAME = "links.txt"
links_file_name = input("File name for URL list [DEFAULT = \"" + DEFAULT_LINKS_FILE_NAME + "\"]: ").strip()
if not links_file_name:
    links_file_name = DEFAULT_LINKS_FILE_NAME
LINKS_FILE_NAME = links_file_name

LINKS_FILE_PATH = OUTPUT_BASE_DIR_PATH + LINKS_FILE_NAME

# If there is no folder, create it
if (not(os.path.isdir(OUTPUT_FOLDER_PATH))):
    os.mkdir(OUTPUT_FOLDER_PATH)

# youtube-dl changes some special characters to underscore: for comparison purposes, we store them in a list
CHAR_TO_CHANGE_LIST = {
    '|': '_',
    '\\': ' ',
    '/': '_',
    ':': ' ',
    '"': '\''
}

equivalent_mp3_counter = 0
error_links = []

#endregion

#region Functions

def get_mp3(yt_url):
    global error_links
    try:
        video_info = yt_dlp.YoutubeDL().extract_info(url = yt_url, download = False)
    except Exception:
        error_links.append(yt_url)
        return
    else:
        video_title = video_info["title"]

    options = {
        "format": "bestaudio/best",
        "keepvideo": False,
        "outtmpl": OUTPUT_FOLDER_PATH + f"{'%(title)s'}.mp3",
    }

    mp3_file = OUTPUT_FOLDER_PATH + video_title + ".mp3"
    mp3_file_revised = ""
    for char in mp3_file:
        for key, value in CHAR_TO_CHANGE_LIST.items():
            if char == key:
                char = value
        mp3_file_revised += char

    is_mp3_equivalent_existing = os.path.exists(mp3_file_revised)
    with yt_dlp.YoutubeDL(options) as ydl:
        if not is_mp3_equivalent_existing:
            try:
                ydl.download([video_info["webpage_url"]])
            except Exception:
                print(traceback.format_exc())
        else:
            global equivalent_mp3_counter
            equivalent_mp3_counter += 1
            print("\nMP3 equivalent already exists for \"" + video_title + "\" (" + yt_url + ")")

    print("________________________________\n")

#endregion

def main():
    global error_links
    url_set = set()
    try:
        if os.stat(LINKS_FILE_PATH).st_size != 0:
            with open(LINKS_FILE_PATH, "r+") as url_file:
                lines = url_file.readlines()
                for line in lines:
                    if not line.isspace() and line not in url_set:
                        url_set.add(line)
        else:
            print("WARNING - Your links file is empty, hence not containing any link to convert.")
    except FileNotFoundError:
        print(traceback.format_exc() + "^^^^ Please create a file to store your YT links (DEFAULT = \"" + DEFAULT_LINKS_FILE_NAME + "\")")

    is_program_reexecuting = True
    while is_program_reexecuting:
        for url in url_set:
            get_mp3(url)

        if equivalent_mp3_counter >= 5:
            print("\n\nPlease clean up your URL list to speed up the MP3 conversion process\nNumber of files already downloaded: " + str(equivalent_mp3_counter))
        
        error_links_counter = len(error_links)
        if error_links_counter > 0:
            if error_links_counter == 1:
                video_s = "video"
                its_their = "its"
            print("The program had problem downloading the audio from %i %s." % (error_links_counter, video_s))
            while True:
                user_input = input("Try %s download again? Y/n " % its_their)
                if str.lower(user_input) == 'n':
                    is_program_reexecuting = False
                    break
                elif str.lower(user_input) == 'y':
                    error_links = []
                    break
                else:
                    print("Please enter 'Y' or 'n'.")
        else:
            is_program_reexecuting = False
    
    if len(error_links):
        file = "utility\\" + re.sub("[':', ' ', '\-', '.']", "", str(datetime.now()))[:-6] + " Problematic URL list.txt"
        with open(file, "w") as error_links_file:
            error_links_file.write("".join([url for url in error_links]))
    else:
        file = "utility\\" + re.sub("[':', ' ', '\-', '.']", "", str(datetime.now()))[:-6] + " SAVE links.txt"
        with open(LINKS_FILE_NAME, "r+") as links_txt, open(file,"w") as save_links_txt:
            for line in links_txt:
                save_links_txt.write(line)
            links_txt.truncate(0)
            
    input("END of the program. Please press Enter to exit.")



if __name__ == "__main__":
    main()
