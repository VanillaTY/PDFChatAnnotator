# 🛠️ PDFChatAnnotator · 文件预处理教程（需 GPU 支持）

---

## 📌 使用前须知

- **文件预处理过程依赖 GPU**，请确保当前环境具备 GPU 支持并已正确安装 CUDA 驱动。
- 若存在 **多块 GPU**，请在 `preprocess.py` 文件中设置：

  ```python
  os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 指定使用第 0 号 GPU
  ```

  其中的 `"0"` 可根据实际需要修改为对应 GPU 的编号。

---

## 📚 步骤详解

### ✅ Step 1：准备待处理 PDF 文件

1. 进入目录：

   ```
   file-preprocess/pdfFiles
   ```

2. 在该目录下**新建一个文件夹**（例如：`my_paper`），并将你需要处理的 PDF 文件放入该文件夹中。

---

### ✅ Step 2：配置 `preprocess.py` 脚本

打开项目中的：

```
file-preprocess/preprocess.py
```

根据你的实际情况，修改以下变量：

| 变量名               | 示例值                | 说明                                          |
| -------------------- | --------------------- | --------------------------------------------- |
| `pdf_store_dir`      | `"pdfFiles/my_paper"` | 设置为你刚刚创建的文件夹路径                  |
| `uploaded_file_name` | `"myfile.pdf"`        | 设置为你要处理的 PDF 文件名                   |
| `pageNum`            | `1`                   | 设置处理的起始页码（从 1 开始）               |
| `endPageNum`         | `10`                  | 设置处理的结束页码                            |
| `isChSim`            | `True`                | 是否为简体中文：是设为 `True`，否设为 `False` |

⚙️ 如需使用指定 GPU，可确保在代码开头设置以下语句：

```python
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
```

---

### ✅ Step 3：运行预处理脚本

激活你的 Conda 环境（例如 `pdfannotator`），在 file-preprocess 目录下运行脚本：

```bash
conda activate pdfannotator
cd file-preprocess
python preprocess.py
```

📌 成功执行后，程序会自动提取文本和图像，并保存至对应目录。

---

### ✅ Step 4：查看输出结果

处理完成后，相关结果将保存在以下路径中：

| 路径                                 | 内容                                 |
| ------------------------------------ | ------------------------------------ |
| `file-preprocess/app/extracted_text` | 提取的文本，以及文字与图片的对应关系 |
| `file-preprocess/app/loadedImgs`     | 从 PDF 中提取的图片                  |
| `file-preprocess/app/pdf_image`      | 中间处理用的临时图片，可忽略         |

---

### ✅ Step 5：手动移动处理结果至 `static` 目录

为使系统能正确读取预处理结果，请**手动执行以下操作**：

- 将`app/extracted_text`目录下的文件复制到`static/app/extracted_text`目录下。
- 将`app/loadedImgs`目录下的图片复制到`static/app/loadedImgs`目录下。
- 将`app/pdf_image`目录下的文件复制到`static/app/pdf_image`目录下。

---

### ✅ Step 6：在网页中使用

现在你已经完成了所有预处理步骤 🎉！

1. 在项目根目录启动主程序（如使用 Django，则运行：`python manage.py runserver`）
2. 打开网页：http://127.0.0.1:8000
3. 在页面上的「文件选择」处，选择你刚刚预处理的 PDF 文件
4. 即可开始进行交互式标注和问答！

---

## 📝 常见问题（FAQ）

- **Q：可以处理多份 PDF 吗？**  
  当前仅支持单个文件处理。可重复上述步骤，或编写简单脚本批量执行。
- **Q：我没有 GPU 可以运行吗？**  
  当前处理依赖 GPU，后续将支持 CPU 模式，敬请关注项目更新。

-
