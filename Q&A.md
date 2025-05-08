# PDFChatAnnotator 常见问题解答

## 目录

- [环境配置问题](#环境配置问题)
- [文件路径问题](#文件路径问题)
- [依赖安装问题](#依赖安装问题)
- [预处理问题](#预处理问题)
- [服务器运行问题](#服务器运行问题)

## 环境配置问题

### 问题 1：Conda 环境激活失败

**错误信息**：`CondaError: Run 'conda init' before 'conda activate'`

**解决方案**：

#### ✅ 解决步骤（一步一步来）

##### ✅ 第一步：以管理员身份打开 CMD 命令行

1. 点击左下角的 **开始菜单**
2. 输入 **cmd**
3. 在搜索结果中，**右键点击**"命令提示符"，选择 **"以管理员身份运行"**

> ⚠️ 必须是管理员身份，否则初始化可能失败

##### ✅ 第二步：执行 Conda 初始化命令

在打开的命令行中输入以下命令：

```
conda init
```

执行后你会看到类似下面的输出，表示它修改了一些启动配置文件：

```
no change     C:\Users\你的用户名\.bashrc
no change     C:\Users\你的用户名\.bash_profile
no change     C:\Users\你的用户名\.profile
modified      C:\Users\你的用户名\.condarc
modified      C:\Users\你的用户名\.bashrc
...
```

然后**关闭这个命令行窗口**

##### ✅ 第三步：重新打开命令行，激活环境

1. **正常方式**打开一个新的命令行窗口（不需要管理员权限）
2. 输入你想激活的环境，例如：

```
conda activate pdfannotator
```

如果一切设置正确，你会看到环境名称出现在命令行前面，例如：

```
(pdfannotator) C:\Users\你的用户名>
```

说明激活成功 ✅！

## 文件路径问题

### 问题 1：运行 python manage.py runserver 时出错

**错误信息**：`[Errno 2] No such file or directory`

**解决方案**：

1. 查看当前目录下的文件：
   - Windows: 输入 `dir` 查看
   - Mac: 输入 `ls` 查看
2. 如果找不到 manage.py，需要：
   - 使用 `cd ../` 返回上一级目录
   - 或使用 `cd ./具体目录名` 进入指定目录

**解决方案简易版**：推荐直接用 VSCode 打开项目根目录（包含 manage.py 文件的目录），在 VSCode 中打开终端，运行命令 python manage.py runserver

### 问题 2：找不到 requirements.txt

**错误信息**：`ERROR: Could not open requirements file: [Errno 2] No such file or directory requirements.txt`

**解决方案**：

- 确保在正确的目录下运行命令
- 如果从 Github 下载，确保在`PDFChatAnnotator-main`目录下
- 使用 VSCode 打开`PDFChatAnnotator-main`文件夹，参考问题：找不到 requirements.txt

## 依赖安装问题

### 问题 1：模块未找到

**错误信息**：`ModuleNotFoundError: No module named 'XXX'`

**解决方案**：

1. 多按几次`Ctrl + C`退出当前运行
2. 执行 `pip install 'XXX'`（XXX 为具体模块名）
3. 或重新执行 `pip install -r requirements.txt`，参考

## 预处理问题

### 问题 1：preprocess.py 运行问题

**解决方案**：

- ⚠️⚠️ 使用最新版本的 preprocess.py 文件
- 从以下地址获取代码：https://github.com/VanillaTY/PDFChatAnnotator/blob/main/file-preprocess/preprocess.py

### 问题 2：Windows 路径转义问题

**错误信息**：`SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \uxxxxxxxx escape`

**解决方案**：

- 在路径前加`r`前缀，例如：

```python
pdf_store_dir = r"C:\Users\Desktop\PDFChatAnnotator-main\file-preprocess\pdfFiles\my_paper"
```

### 问题 3：变量未定义错误

**错误信息**：`UnboundLocalError: local variable 'endPageNum' referenced before assignment`

**解决方案**：

- 更新 preprocess.py 文件到最新版本，使用最新版本的 preprocess.py 文件，参考 问题 1：preprocess.py 运行问题

### 问题 4：GPU 内存不足

**错误信息**：`torch.OutOfMemoryError: CUDA out of memory. Tried to allocate XXX MiB. GPU 0 has a total capacity of XXX GiB of which 0 bytes is free. Of the allocated memory 1011.48 MiB is allocated by PyTorch, and 22.52 MiB is reserved by PyTorch but unallocated.`

**解决方案**：

- GPU 显存带不起来导致的，可以在服务器或者别的电脑上单独做预处理这个步骤
- 然后把生成好的 JSON 文件按照教程挪到自己的电脑上，然后进行后续的标注也是 OK 的

### 问题 5：JSON 解析错误

**错误信息**：`JSONDecodeError: Expecting value: line 1 column 2 (char 1)`

**解决方案**：

1. 这个问题是因为之前预处理过程非正常终止，导致生成了一个报废的 JSON 文件
2. 所以要把这个没生成完的 JSON 文件删掉
3. 去 file-preprocess/app/extracted_text 目录下，删掉报错的 JSON 文件
4. 去 file-preprocess/app/extracted_text 目录下的方法：VSCode 左侧文件列表找到 static，一路往下找

## 服务器运行问题

### 问题 1：使用 python manage.py runserver 启动服务器失败

**错误信息**：`[Errno 2] No such file or directory`

**解决方案**：

- 确保在项目根目录（包含 manage.py 的目录）下运行命令
- 使用 VSCode 打开项目根目录，在终端中运行`python manage.py runserver`
