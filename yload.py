import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouDown")
        self.root.geometry("530x330")
        self.save_path = tk.StringVar(value="./")
        self.download_speed = tk.StringVar(value="0 KB/s")
        self.avg_speed = tk.StringVar(value="N/A")
        self.progress = tk.DoubleVar(value=0)
        self.theme = "light"
        self.init_ui()

    def init_ui(self):
        # URL Input
        tk.Label(self.root, text="YouTube Link:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=2)

        # Download Type
        self.download_type = tk.StringVar(value="mp3")
        tk.Label(self.root, text="Download Type:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Radiobutton(self.root, text="MP3", variable=self.download_type, value="mp3").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Video", variable=self.download_type, value="video").grid(row=2, column=1, sticky="w")

        # Save Path
        tk.Label(self.root, text="Save Path:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        save_path_entry = tk.Entry(self.root, textvariable=self.save_path, width=40)
        save_path_entry.grid(row=3, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.select_path).grid(row=3, column=2, padx=10, pady=10)

        # Progress Bar
        ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate", variable=self.progress).grid(
            row=4, column=0, columnspan=3, padx=10, pady=10
        )

        # Download Speed
        tk.Label(self.root, text="Download Speed:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        tk.Label(self.root, textvariable=self.download_speed).grid(row=5, column=1, padx=10, pady=10, sticky="w")

        # Average Speed
        tk.Label(self.root, text="Average Speed:").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        tk.Label(self.root, textvariable=self.avg_speed).grid(row=6, column=1, padx=10, pady=10, sticky="w")

        # Download Button
        tk.Button(self.root, text="Download", command=self.start_thread).grid(row=7, column=0, columnspan=3, pady=10)


    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path.set(path)

    def start_thread(self):
        thread = threading.Thread(target=self.start_download)
        thread.start()

    def start_download(self):
        video_url = self.url_entry.get().strip()
        if not video_url:
            messagebox.showerror("Error", "Please enter a YouTube link.")
            return
        download_type = self.download_type.get()
        opts = self.get_download_options(download_type)

        self.progress.set(0)
        self.download_speed.set("0 KB/s")
        self.avg_speed.set("N/A")

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            messagebox.showinfo("Success", f"{download_type.upper()} downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def get_download_options(self, download_type):
        options = {
            "format": "bestaudio/best" if download_type == "mp3" else "best",
            "outtmpl": f"{self.save_path.get()}/%(title)s.%(ext)s",
            "progress_hooks": [self.update_progress],
        }
        if download_type == "mp3":
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        return options

    def update_progress(self, d):
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes", 0)
            speed = d.get("speed", 0)
            self.progress.set((downloaded / total) * 100 if total else 0)
            self.download_speed.set(f"{round(speed / 1024, 2)} KB/s" if speed else "0 KB/s")
        elif d["status"] == "finished":
            self.progress.set(100)
            avg_speed = d.get("elapsed", 1)  # Avoid division by zero
            avg_speed_calc = (d.get("total_bytes", 0) / 1024) / avg_speed
            self.avg_speed.set(f"{round(avg_speed_calc, 2)} KB/s")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
