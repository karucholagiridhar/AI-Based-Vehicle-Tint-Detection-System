

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageTk

# --------------------------------------------------
# Inference Client Init
# --------------------------------------------------

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="cto2SFwA0t7Z5g5qqOQi"
)

MODEL_ID = "tinted-car-windows-mkpc6-ctdz6/2"


# --------------------------------------------------
# Resize image to avoid 413 error
# --------------------------------------------------

def resize_for_api(path, max_w=1280):

    img = cv2.imread(path)
    h, w, _ = img.shape

    if w > max_w:
        scale = max_w / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h))

    temp_path = "temp_upload.jpg"
    cv2.imwrite(temp_path, img)

    return temp_path


# --------------------------------------------------
# Tkinter UI
# --------------------------------------------------

root = tk.Tk()
root.title("🚗 Government-Grade Enforcement & Compliance Monitoring")
root.geometry("1400x760")
root.configure(bg="#111827")

title = tk.Label(
    root,
    text="AI Tinted Car Window Detector",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#111827"
)
title.pack(pady=10)

main_frame = tk.Frame(root, bg="#111827")
main_frame.pack()

left_frame = tk.Frame(main_frame, bg="#111827")
left_frame.grid(row=0, column=0, padx=25)

right_frame = tk.Frame(main_frame, bg="#111827")
right_frame.grid(row=0, column=1, padx=25)

tk.Label(left_frame, text="INPUT IMAGE",
         font=("Arial", 14, "bold"),
         fg="white", bg="#111827").pack()

tk.Label(right_frame, text="OUTPUT IMAGE",
         font=("Arial", 14, "bold"),
         fg="white", bg="#111827").pack()

input_label = tk.Label(left_frame, bg="#1f2933")
input_label.pack(pady=10)

output_label = tk.Label(right_frame, bg="#1f2933")
output_label.pack(pady=10)


# --------------------------------------------------
# Globals
# --------------------------------------------------

current_input = None
current_output = None


# --------------------------------------------------
# Upload + Detect
# --------------------------------------------------

def upload_and_detect():

    global current_input, current_output

    path = filedialog.askopenfilename(
        filetypes=[("Images", "*.jpg *.jpeg *.png")]
    )

    if not path:
        return

    try:
        # ---------- Show INPUT ----------
        orig = Image.open(path)
        orig_disp = orig.resize((600, 420))
        tk_orig = ImageTk.PhotoImage(orig_disp)

        input_label.configure(image=tk_orig)
        input_label.image = tk_orig

        current_input = path

        # ---------- Resize before sending ----------
        resized_path = resize_for_api(path)

        # ---------- Run inference ----------
        result = CLIENT.infer(
            resized_path,
            model_id=MODEL_ID
        )

        preds = result["predictions"]

        img = cv2.imread(resized_path)

        preds = sorted(preds, key=lambda x: x["x"])

        for p in preds:

            x, y = int(p["x"]), int(p["y"])
            w, h = int(p["width"]), int(p["height"])

            cls = p["class"]
            conf = int(p["confidence"] * 100)

            label = f"{cls} {conf}%"

            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)

            # 🎨 Colors like Roboflow UI
            if cls == "tinted":
                color = (255, 0, 255)   # pink/red
            else:
                color = (180, 0, 255)   # purple

            # Draw box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)

            # Label bg
            (tw, th), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, 2)

            cv2.rectangle(
                img,
                (x1, y1 - th - 10),
                (x1 + tw + 8, y1),
                color, -1)

            # Label text
            cv2.putText(
                img,
                label,
                (x1 + 4, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2)

        # ---------- Save OUTPUT ----------
        out_path = "tinted_output.jpg"
        cv2.imwrite(out_path, img)
        current_output = out_path

        # ---------- Show OUTPUT ----------
        out_img = Image.open(out_path)
        out_disp = out_img.resize((600, 420))
        tk_out = ImageTk.PhotoImage(out_disp)

        output_label.configure(image=tk_out)
        output_label.image = tk_out

        messagebox.showinfo(
            "Detection Complete",
            f"Windows detected: {len(preds)}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# --------------------------------------------------
# Save Button
# --------------------------------------------------

def save_output():

    if not current_output:
        messagebox.showwarning(
            "No Output",
            "Run detection first!"
        )
        return

    dest = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("JPEG", "*.jpg")]
    )

    if dest:
        Image.open(current_output).save(dest)
        messagebox.showinfo(
            "Saved",
            f"Output saved to:\n{dest}"
        )


# --------------------------------------------------
# Buttons
# --------------------------------------------------

btn_frame = tk.Frame(root, bg="#111827")
btn_frame.pack(pady=18)

upload_btn = tk.Button(
    btn_frame,
    text="Upload Image",
    command=upload_and_detect,
    bg="#22c55e",
    fg="white",
    font=("Arial", 14),
    width=18)

upload_btn.grid(row=0, column=0, padx=18)

save_btn = tk.Button(
    btn_frame,
    text="Save Output",
    command=save_output,
    bg="#3b82f6",
    fg="white",
    font=("Arial", 14),
    width=18)

save_btn.grid(row=0, column=1, padx=18)


root.mainloop()
