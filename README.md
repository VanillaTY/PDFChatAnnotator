# PDFChatAnnotator

**PDFChatAnnotator**: A Human-LLM Collaborative Multi-Modal Data Annotation Tool for PDF-Format Catalogs.

🌏 [简体中文 / Chinese Version](./README.zh.md)

## 📝 Description

**PDFChatAnnotator** is a collaborative annotation tool that leverages the strengths of both human experts and Large Language Models (LLMs) to annotate multi-modal data in PDF-format catalogs. It is designed to streamline and enhance the annotation process through interactive workflows and intelligent suggestions.

📄 **Related Publication**:

This project is based on our research paper published at ACM IUI 2024:  
[PDFChatAnnotator: A Human-LLM Collaborative Multi-Modal Data Annotation Tool for PDF-Format Catalogs](https://dl.acm.org/doi/abs/10.1145/3640543.3645174)

### 📌 Version Update

**Current Version: 2.0**

- In version 1.0, data was saved to a MySQL database, which required additional setup and configuration.
- In version 2.0, to simplify the installation and usage process—especially for non-computer science users—we have switched to saving annotation results directly into Excel files (`.xlsx` format).  
  This change makes the tool more accessible and easier to use out of the box.

### 📊 System Overview

![Workflow Overview](./public/images/overview.png)

### 🖍️ Interactive Annotation Interface

![Interactive Annotation](./public/images/interactive-annotation.png)

## ⚙️ Installation

### Prerequisites

- Python 3.9
- Anaconda (recommended for environment management)
- Visual Studio Code (recommended IDE)

### 1. Download and Set Up the Project

1. Download the project:

   - Visit: https://github.com/VanillaTY/PDFChatAnnotator
   - Click the green `Code` button and select `Download ZIP`
   - Extract the ZIP file to your preferred location (e.g., Desktop)

2. Open the project in VS Code:
   - Drag the extracted folder into VS Code
   - If prompted with "Do you trust the authors?", select "Yes"

### 2. Set Up Python Environment

#### Using Anaconda (Recommended)

1. Install Anaconda:

   - Download from: https://www.anaconda.com/download
   - Follow the installation wizard
   - For Windows users: Add Anaconda to system PATH during installation

2. Create and activate the environment:
   ```bash
   conda create -n pdfannotator python=3.9
   conda activate pdfannotator
   ```

### 3. Install Dependencies

1. Install project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Install OS-specific dependencies:
   - **Windows**:
     ```bash
     pip install pyreadline3
     ```
   - **macOS**:
     ```bash
     pip install readline
     ```

### 4. Configure API Key

1. Obtain your API key:

   - Visit: https://api.chatanywhere.tech/#/
   - Purchase a plan and get your API key

2. Configure the API key:
   - Open `utils/prompt.py`
   - Replace the placeholder with your API key:
     ```python
     api_key = "your_api_key_here"
     base_url = "your_base_url_here"
     ```

## 🚀 Running the Application

1. Activate the environment:

   ```bash
   conda activate pdfannotator
   ```

2. Start the development server:

   ```bash
   python manage.py runserver
   ```

3. Access the application:
   - Open your browser
   - Navigate to: http://127.0.0.1:8000/

## 📄 PDF Preprocessing (Required Before Use)

Before launching the system, you **must preprocess your PDF file(s)** to extract necessary text and image data.

Please follow the guide below **before running the application**:

- 📘 [中文预处理教程](./file-preprocess/README.md)
- 📙 [English Preprocessing Guide](./file-preprocess/README.en.md)

The preprocessing process requires a **GPU-supported environment** and will prepare the data required for annotation.

## 📌 Quick Start Guide

For daily use:

1. Open VS Code and load the project
2. Open terminal and run:
   ```bash
   conda activate pdfannotator
   python manage.py runserver
   ```
3. Access http://127.0.0.1:8000/ in your browser

For more detailed installation instructions, please refer to the [Installation Guide](./安装教程小白版.md).
