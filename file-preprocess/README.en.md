# 🛠️ PDFChatAnnotator · Preprocessing Tutorial (GPU Required)

---

## 📌 Before You Start

- **This preprocessing process requires a GPU**. Please make sure your current environment supports CUDA and the necessary GPU drivers are installed.
- If you have **multiple GPUs**, specify which one to use by setting this in the `preprocess.py` file:

```python
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Use GPU #0
```

You can modify `"0"` to the GPU ID you want to use.

---

## 📚 Step-by-Step Instructions

### ✅ Step 1: Prepare the PDF Files

1. Navigate to the directory:

```
file-preprocess/pdfFiles
```

2. Create a **new folder** (e.g., `my_paper`) inside this directory and put your PDF file(s) into the folder.

---

### ✅ Step 2: Configure the `preprocess.py` Script

Open:

```
file-preprocess/preprocess.py
```

Modify the following variables based on your own setup:

| Variable Name        | Example Value         | Description                                                              |
| -------------------- | --------------------- | ------------------------------------------------------------------------ |
| `pdf_store_dir`      | `"pdfFiles/my_paper"` | Path to the folder you just created                                      |
| `uploaded_file_name` | `"myfile.pdf"`        | Name of the PDF file you want to process                                 |
| `pageNum`            | `1`                   | Starting page number (starts from 1)                                     |
| `endPageNum`         | `10`                  | Ending page number                                                       |
| `isChSim`            | `True`                | Is the content in Simplified Chinese? Set `True` for Yes, `False` for No |

⚙️ If you want to use a specific GPU, ensure this line is present at the beginning of the script:

```python
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
```

---

### ✅ Step 3: Run the Preprocessing Script

Activate your Conda environment (e.g., `pdfannotator`) and run the script from the `file-preprocess` directory:

```bash
conda activate pdfannotator
cd file-preprocess
python preprocess.py
```

📌 Upon success, the script will automatically extract text and images and save them to the corresponding directories.

---

### ✅ Step 4: Check Output Results

After the script completes, you can find the results in these directories:

| Path                                 | Content                                        |
| ------------------------------------ | ---------------------------------------------- |
| `file-preprocess/app/extracted_text` | Extracted text and text-image relationships    |
| `file-preprocess/app/loadedImgs`     | Images extracted from the PDF                  |
| `file-preprocess/app/pdf_image`      | Temporary intermediate images (can be ignored) |

---

### ✅ Step 5: Manually Move Results to the `static` Directory

To ensure the system can properly read the preprocessed data, **manually perform the following actions**:

- Copy files from `app/extracted_text` to `static/app/extracted_text`
- Copy images from `app/loadedImgs` to `static/app/loadedImgs`
- Copy files from `app/pdf_image` to `static/app/pdf_image`

---

### ✅ Step 6: Use in Web Interface

You're now ready to go 🎉!

1. In the project root directory, launch the main application (for example, with Django):

   ```bash
   python manage.py runserver
   ```

2. Open your browser and go to: http://127.0.0.1:8000
3. Use the “File Selection” section to select the PDF file you just preprocessed
4. You can now begin interactive annotation and Q&A!

---

## 📝 Frequently Asked Questions (FAQ)

- **Q: Can I process multiple PDF files?**  
  Currently, only single-file processing is supported. You can repeat the steps above or write a simple script for batch processing.

- **Q: Can I run this without a GPU?**  
  Currently, a GPU is required. CPU support will be available in future updates.

---
