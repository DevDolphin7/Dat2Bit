import configparser, io
import DOerrorLogging as log
import dat.version as dev_info
import tkinter as tk
import customtkinter as ctk
from dat import dat_main as data_main
from PIL import Image, ImageTk



class GenerateUI():

    def __init__(self):
        # Start log file
        log.log_exc(f"App version {dev_info.__version__} started", level=20)

        # Create Window
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("./ctktheme.json")

        self.root = ctk.CTk()
        self.root.geometry("480x480")
        self.root.configure(bg='white')
        self.root.title("Dat2Bit: a Dolphin Creation!")
        self.root.iconbitmap('./dat/Dat2BitIcon.ico')
        self.root.resizable(False,False)

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.pack(fill="both",expand=True)


        # Set class variables
        self.config_file_path = './config.ini'
        self.dat = data_main.Data()
        self.file_selected = False
        self.output_dir_selected = False
        
        # Initiate function class
        self.dat_to_bit = DatToBit()

        # Try to load user config
        if not self.load_config_file():
            self.file_types = (('All files', '*.*'), ('Portable Network Graphic', '*.png'))
            self.initial_dir_data = "./Examples/"
            self.initial_dir_output = "./"

        self.save_config_file()

        # Load background and user interface items
        self.create_bg()
        self.create_ui()

        self.root.mainloop()


    def load_config_file(self):
        """Returns True if successful, False if not"""
        config = configparser.ConfigParser()

        try:
            config.read(self.config_file_path)

            # Load variables
            self.file_types = tuple(tuple(map(str.strip, tpl.strip('()').split(','))) for tpl in config.get('Settings', 'File Types').split('|'))
            self.initial_dir_data = str(config.get('Settings', 'Initial Data File Directory'))
            self.initial_dir_output = str(config.get('Settings', 'Initial Output Directory'))
            
            return True
        
        except Exception as e:
            log.log_exc(f"Error loading configuration file 'config.ini'")
            return False


    def save_config_file(self):
        config = configparser.ConfigParser()
        config['User Information'] = {'Top': "This is the config file for the Dat2Bit applicaiton writted by DevDolphin7.",
                                      'General': "The values of this config file can be manually adjusted below, or they automatically update as you use the app.",
                                      'Information': "If for any reason the app cannot load these values, it defaults to the values defined in the source code. It will inform you if it does this.",
                                      'Warning': "Manual editing is encouraged but may lead to errors. See 'README.txt' to reset config.ini if this is the case.",
                                      'Further Help': "For further help go to https://github.com/DevDolphin7/Dat2Bit"}
        config['Settings'] = {'File Types': '|'.join([f'({name},{pattern})' for name, pattern in self.file_types]),
                              'Initial Data File Directory': self.initial_dir_data,
                              'Initial Output Directory': self.initial_dir_output}
        try:
            with WithOpenFile(self.config_file_path, "a", config=True) as config_file:
                config.write(config_file)

            return True
        except Exception as e:
            # Update user about error
            log.log_exc("Error saving configuration file 'config.ini'")
            tk.messagebox.showinfo("Configuration Error Occured",f"Error saving configuration file 'config.ini'.\n\nError information: {e}")
            return False


    def create_bg(self):
        # Load bg image from .py files
        b = bytearray(self.dat.data("DTBbg"))
        self.bgPicImg = Image.open(io.BytesIO(b))
        self.bgPic = ImageTk.PhotoImage(image=self.bgPicImg)

        # Set bg pic as window bg
        self.bg_container = self.canvas.create_image(240,240,image=self.bgPic)
        self.canvas.pack(fill="both",expand=True) 


    def create_ui(self):
        self.open_file_button = ctk.CTkButton(self.root, text="Select Image",command=self.select_file)
        self.canvas.create_window(140, 20, anchor="nw", window=self.open_file_button, width=105, height=30)
        self.output_dir_button = ctk.CTkButton(self.root,text="Save Location",command=self.select_output_dir)
        self.canvas.create_window(140, 60, anchor="nw", window=self.output_dir_button, width=105, height=30)
        self.convert_button = ctk.CTkButton(self.root,text="Create .py", fg_color="#FF6961",command=self.check_convert)
        self.canvas.create_window(260, 20, anchor="nw", window=self.convert_button, width=85,height=70)


    def select_file(self):
        self.file_to_convert = tk.filedialog.askopenfilename(title='Select a data file', initialdir=self.initial_dir_data,filetypes=self.file_types)
        if self.file_to_convert == "":
            log.log_exc("Select file window closed with no file selected.", level=20)
            if log.check_log_repeat_info(look_for="Select file window closed with no file selected."):
                tk.messagebox.showinfo(title='Warning',message="Warning: No file selected!")
        else:
            self.file_selected = True
            self.dat_to_bit.file_to_convert = self.file_to_convert
            if self.output_dir_selected: self.convert_button.configure(fg_color="green")
            self.initial_dir_data = self.file_to_convert[0:self.file_to_convert.rfind("/")+1]
            self.save_config_file()


    def select_output_dir(self):
        output_dir = tk.filedialog.askdirectory(title='Choose where to save the file', initialdir=self.initial_dir_output) + "/"
        if output_dir == "/":
            log.log_exc("Select output location window closed with no folder selected.", level=20)
            if log.check_log_repeat_info(look_for="Select output location window closed with no folder selected."):
                tk.messagebox.showinfo(title='Warning',message="Warning: No folder selected!")
        else:
            self.output_dir_selected = True
            self.initial_dir_output = output_dir
            self.dat_to_bit.output_dir = output_dir
            if self.file_selected: self.convert_button.configure(fg_color="green")
            self.save_config_file()


    def check_convert(self):
        # Check file has been selected prior to convert
        if not self.file_selected:
            log.log_exc("Attempted convert with no file selected.", level=20)
            if log.check_log_repeat_info(look_for="Select output location window closed with no folder selected."):
                tk.messagebox.showinfo(title='Warning',message="Warning: No file selected!")
        # Check output directory has been selected
        elif not self.output_dir_selected:
            log.log_exc("Attempted convert with no folder selected.", level=20)
            if log.check_log_repeat_info(look_for="Select output location window closed with no folder selected."):
                tk.messagebox.showinfo(title='Warning',message="Warning: No folder selected!")
        # If all is well run the convert class
        else:
            convert_success = self.dat_to_bit.convert_dat_to_py()
            if convert_success == True:
                log.log_exc(f"Successfully converted {self.file_to_convert} to .py", level=20)
                tk.messagebox.showinfo(title='Success', message=f"Successfully converted {self.file_to_convert} to .py")
                self.save_config_file()
            else:
                log.log_exc(f"An unknown error occured while converting {self.file_to_convert} to .py")
                tk.messagebox.showinfo(title='Error Occured',message=f"An error occured: {convert_success}")
                



        

class DatToBit():

    def __init__(self):
        self.file_to_convert = ""
        self.output_dir = ""

    def convert_dat_to_py(self):
        """Returns True is successful, False if not"""
        try:
            with WithOpenFile(self.file_to_convert, "rb") as data_file:
                b = data_file.read()
            b = str(b)
            b = b[2:len(b)-1]

            # Get file name
            self.given_file_name = self.file_to_convert[self.file_to_convert.rfind("/")+1:self.file_to_convert.rfind(".")]
            with WithOpenFile(f"{self.output_dir}{self.given_file_name}.py", "w") as output:
                output.write(f"def data():\n    data = \"\"\"{str(b)}\"\"\"\n    return data.encode('latin-1')")
        except Exception as e:
            return e
        return True
        




class WithOpenFile():
    def __init__(self, output_path, mode, config=False):
        if config:
            self.output_path = "./config.ini"
        else:
            self.output_path = output_path
        self.mode = mode
        self.config = config

    def __enter__(self):
        # Open the file in write mode first to remove any prior content, then open in append
        if self.config:
            self.f = open(self.output_path,'w')
            self.f.close()
        self.f = open(self.output_path, self.mode)
        return self.f

    def __exit__(self, *args):
        self.f.close()
        if any(args):
            # An exception occurred
            exc_type, exc_value, traceback_str = args
            formatted_traceback = traceback.format_tb(traceback_str)[0]
            log_exc(f"An error occured while handling the file:\n{self.output_path}")
            messagebox.showinfo(title='File Handling Error Occured',message=f"An error occured while handling the {self.output_path} file.\n\nError type: {exc_type}\nError value: {exc_value}")





GenerateUI()
