/**
 * PDF Viewer Module
 * Handles PDF loading, rendering, and interaction functionality
 */

// ==================== Global Variables ====================
var default_scale; // Default scale for PDF rendering
var ifscaled = false; // Flag indicating if PDF is currently scaled
var now_scale; // Current scale of PDF
var draggableCanvasId; // ID of the currently draggable canvas
var isScaledCanvasDragging = false; // Flag for canvas drag state
var scaledCanvasOffset = { x: 0, y: 0 }; // Offset for canvas dragging

// ==================== PDF Display Control Functions ====================

/**
 * Controls the display of PDF pages in the preview container
 * @param {number} currentPage - The page number to display
 */
var canvasDisplayController = async (currentPage) => {
  console.log(`step2: display ${currentPage}`);
  const pdfPreview = document.getElementById("pdf-preview");
  console.log(pdfPreview.children.length);
  await Array.from(pdfPreview.children).forEach((dom, index) => {
    console.log(`step2: ${index}, ${dom.id}`);
    if (dom.id === "canvas" + currentPage) {
      dom.style.display = "block";
    } else {
      dom.style.display = "none";
    }
  });
  document.getElementById("pdf-pageNum-current").value = currentPage;
  console.log("step2 end");
};

/**
 * Loads a PDF file and returns the loaded PDF object
 * @returns {Promise<Object>} The loaded PDF object
 */
var loadingPDF = async () => {
  const pdfData = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsArrayBuffer(pdfObject.getPdf);
    reader.onload = (event) => resolve(new Uint8Array(event.target.result));
    reader.onerror = (error) => reject(error);
  });

  const loadingTask = pdfjsLib.getDocument({ data: pdfData });

  // const loadedPdf = await loadingTask.promise.then((loadedPdf)=> loadedPdf);
  const loadedPdf = await loadingTask.promise.then(async function (pdf) {
    pdfObject.setPdfLength = pdf._pdfInfo.numPages;
    return pdf;
    //
    //             await pdf.getPage(pageNum).then(function (page) {
    //                 let scale = 1;
  });
  console.log("loadedPdf end");
  return loadedPdf;
};

/**
 * Loads and renders a specific page of the PDF
 * @param {Object} loadedPdf - The loaded PDF object
 * @param {number} pageNum - The page number to load
 * @param {number} scale - The scale factor for rendering
 */
var loadingCanvasPage = async (loadedPdf, pageNum, scale = default_scale) => {
  console.log(`-------- step 3: ${pageNum} Start------------`);
  if (pageNum < 1 || pageNum > pdfObject.getPdfLength) {
    return;
  }
  const pdfPreview = document.getElementById("pdf-preview");

  try {
    let page = await loadedPdf.then((value) =>
      value.getPage(pageNum).then(function (page) {
        console.log("loadingCanvasPage", page);
        return page;
      })
    );
    // let page = await loadedPdf.getPage(pageNum).then(function (page) {
    //     return page;
    // })

    let viewport;
    if (default_scale === undefined) {
      //page.getViewport() 方法在传递参数名为 scale 时是特殊的，不需要写成 scale: scale 的形式。
      // 这是因为 getViewport() 方法的参数对象中只包含一个属性 scale，
      // 而在 JavaScript 中，如果对象字面量的属性名和变量名相同，可以省略属性名，直接写变量名。
      let scale = 1;
      let tmp_viewport = page.getViewport({ scale });

      let canvas = document.createElement("canvas");

      canvas.height = pdfPreview.offsetHeight;

      let temp_width =
        (tmp_viewport.width / tmp_viewport.height) * pdfPreview.offsetHeight;
      canvas.width =
        temp_width > pdfPreview.offsetWidth
          ? pdfPreview.offsetWidth
          : temp_width;

      let scaledScale = canvas.width / tmp_viewport.width; // 计算缩放比例
      default_scale = scaledScale;
      now_scale = scaledScale;
      // const scaledViewport =  page.getViewport({ scale: scaledScale });
      viewport = page.getViewport({ scale: scaledScale });

      console.log(
        `default_scale === undefined, scale: ${scaledScale}`,
        viewport
      );
    } else {
      viewport = page.getViewport({ scale });
      console.log(`default_scale !== undefined, scale: ${scale}`, viewport);
    }

    const canvas = document.createElement("canvas");

    canvas.height = pdfPreview.offsetHeight;

    let temp_width =
      (viewport.width / viewport.height) * pdfPreview.offsetHeight;
    canvas.width =
      temp_width > pdfPreview.offsetWidth ? pdfPreview.offsetWidth : temp_width;

    canvas.style.marginLeft =
      temp_width > pdfPreview.offsetWidth
        ? "0"
        : (pdfPreview.offsetWidth - temp_width) / 2 + "px";

    if ((scale === default_scale && !ifscaled) || scale === undefined) {
      scale = default_scale;
      canvas.style.display = "none";
      canvas.id = "canvas" + pageNum;
    } else {
      ifscaled = true;
      document.getElementById("canvas" + pageNum).style.display = "none";
      canvas.style.display = "block";
      canvas.id = "canvas" + pageNum + "scaled";
    }

    pdfPreview.appendChild(canvas);

    if (scale === default_scale && !ifscaled) {
      addPdfContainerListener(canvas);
    }

    let scaledScale;
    if (scale === default_scale && !ifscaled) {
      scaledScale = default_scale; // 计算缩放比例
      now_scale = scaledScale;

      const scaledViewport = page.getViewport({ scale: scaledScale });
      const context = canvas.getContext("2d");
      const renderContext = {
        canvasContext: context,
        viewport: scaledViewport,
      };
      await page.render(renderContext);
    } else {
      scaledScale = scale;
      now_scale = scaledScale;
      let scaledViewport = page.getViewport({ scale: scaledScale });

      canvas.height = scaledViewport.height;
      canvas.width = scaledViewport.width;
      canvas.style.marginLeft = "0";
      canvas.style.cursor = "move";
      canvas.style.position = "relative";
      canvas.style.left = "0px";
      canvas.style.top = "0px";
      console.log("add", canvas);
      draggableCanvasId = canvas.id;
      addScaledCanvasListener(canvas.id);

      let context = canvas.getContext("2d");
      const renderContext = {
        canvasContext: context,
        viewport: scaledViewport,
      };

      await page.render(renderContext);
    }

    console.log("loading end");
  } catch (error) {
    console.error("Error loading or rendering PDF:", error);
  } finally {
    console.log(`--------Step3 : PageNum End------------`);
    console.log("step3");
  }
};

// ==================== Canvas Interaction Functions ====================

/**
 * Handles mouse down event for draggable canvas
 * @param {MouseEvent} event - The mouse event
 */
function draggableCanvasMouseDown(event) {
  isScaledCanvasDragging = true;
  scaledCanvasOffset.x = event.clientX;
  scaledCanvasOffset.y = event.clientY;
  // console.log('mousedown', scaledCanvasOffset.x, scaledCanvasOffset.y)
}

/**
 * Handles mouse move event for draggable canvas
 * @param {MouseEvent} event - The mouse event
 */
function draggableCanvasMouseMove(event) {
  if (isScaledCanvasDragging) {
    let draggableCanvas = document.getElementById(draggableCanvasId);
    console.log(
      "(draggableCanvas.style.left + draggableCanvas.style.width)",
      parseInt(draggableCanvas.style.left) + parseInt(draggableCanvas.width)
    );
    draggableCanvas.style.left =
      parseInt(draggableCanvas.style.left) + parseInt(draggableCanvas.width) >
      parseInt(document.getElementById("pdf-preview-container").style.width)
        ? parseInt(draggableCanvas.style.left) +
          event.clientX -
          scaledCanvasOffset.x +
          "px"
        : parseInt(draggableCanvas.style.left) + "px";
    draggableCanvas.style.top =
      parseInt(draggableCanvas.style.top) +
      event.clientY -
      scaledCanvasOffset.y +
      "px";
    scaledCanvasOffset.x = event.clientX;
    scaledCanvasOffset.y = event.clientY;
    // console.log('mousemove', draggableCanvas.style.left, draggableCanvas.style.top)
  }
}

/**
 * Handles mouse up event for draggable canvas
 */
function draggableCanvasMouseUp(event) {
  isScaledCanvasDragging = false;
}

/**
 * Adds event listeners for canvas dragging
 * @param {string} divId - The ID of the canvas element
 */
var addScaledCanvasListener = (divId) => {
  let draggableCanvas = document.getElementById(divId);

  draggableCanvas.addEventListener("mousedown", draggableCanvasMouseDown);

  document
    .getElementById("pdf-preview-container")
    .addEventListener("mousemove", draggableCanvasMouseMove);

  document
    .getElementById("pdf-preview-container")
    .addEventListener("mouseup", draggableCanvasMouseUp);
};

/**
 * Removes event listeners for canvas dragging
 * @param {HTMLElement} draggableCanvas - The canvas element
 */
var removeScaledCanvasListener = (draggableCanvas) => {
  isScaledCanvasDragging = false;
  scaledCanvasOffset.x = 0;
  scaledCanvasOffset.y = 0;
  draggableCanvas.removeEventListener("mousedown", draggableCanvasMouseDown);
  document
    .getElementById("pdf-preview-container")
    .removeEventListener("mousemove", draggableCanvasMouseMove);

  document
    .getElementById("pdf-preview-container")
    .removeEventListener("mouseup", draggableCanvasMouseUp);
};

// ==================== Zoom Control Functions ====================

/**
 * Handles zoom in functionality
 */
var clickZoomInButton = () => {
  console.log("zoom in");
  let pageNum = pdfObject.getCurrentPage;
  // 放大按钮点击事件
  if (now_scale + 0.2 <= 2.0) {
    // 设置最大缩放比例
    if (ifscaled) {
      removeScaledCanvasListener(
        document.getElementById("canvas" + pageNum + "scaled")
      );
      document
        .getElementById("canvas" + pageNum + "scaled")
        .parentElement.removeChild(
          document.getElementById("canvas" + pageNum + "scaled")
        );
    }
    loadingCanvasPage(loadingPdf, pageNum, now_scale + 0.2).then((r) =>
      console.log("success")
    );
  }
};

/**
 * Handles zoom out functionality
 */
var clickZoomOutButton = () => {
  console.log("zoom out");
  let pageNum = pdfObject.getCurrentPage;
  // 放大按钮点击事件
  console.log(now_scale);
  if (now_scale - 0.2 >= 1.0) {
    // 设置最大缩放比例
    if (ifscaled) {
      removeScaledCanvasListener(
        document.getElementById("canvas" + pageNum + "scaled")
      );
      document
        .getElementById("canvas" + pageNum + "scaled")
        .parentElement.removeChild(
          document.getElementById("canvas" + pageNum + "scaled")
        );
    }
    loadingCanvasPage(loadingPdf, pageNum, now_scale - 0.2).then((r) =>
      console.log("success")
    );
  }
};

// ==================== Page Management Functions ====================

/**
 * Removes a canvas element from the preview container
 * @param {number} childNum - The page number of the canvas to remove
 */
var removeCanvasChild = (childNum) => {
  console.log(`step1: remove ${childNum}`);
  const pdfPreview = document.getElementById("pdf-preview");
  if (childNum >= 1 && childNum <= pdfObject.getPdfLength) {
    let removingChild = document.getElementById("canvas" + childNum);
    if (removingChild != null) {
      pdfPreview.removeChild(removingChild);
    }
  }
  console.log("step1 end");
};

/**
 * Loads multiple pages around the current page
 * @param {Object} loadingPdf - The loaded PDF object
 * @param {number} currentPage - The current page number
 */
var batchLoadingCanvasPage = async (loadingPdf, currentPage) => {
  if (document.getElementById("canvas" + currentPage) === null) {
    await loadingCanvasPage(loadingPdf, currentPage);
  }
  for (let i = 1; i <= 10; i++) {
    if (currentPage + i >= 1 && currentPage + i <= pdfObject.getPdfLength) {
      if (document.getElementById("canvas" + (currentPage + i)) === null) {
        await loadingCanvasPage(loadingPdf, currentPage + i);
      }
    }
    if (currentPage - i >= 1 && currentPage - i <= pdfObject.getPdfLength) {
      if (document.getElementById("canvas" + (currentPage - i)) === null) {
        await loadingCanvasPage(loadingPdf, currentPage - i);
      }
    }
  }
};

/**
 * Changes the current PDF page
 * @param {Object} loadingPdf - The loaded PDF object
 * @param {string} direction - The direction to change pages ("left" or "right")
 * @param {number} currentPage - The current page number
 * @param {Function} callback - Callback function to execute after page change
 */
var changePDFPage = async (loadingPdf, direction, currentPage, callback) => {
  if (ifscaled) {
    if (document.getElementById("canvas" + (currentPage - 1) + "scaled")) {
      removeScaledCanvasListener(
        document.getElementById("canvas" + (currentPage - 1) + "scaled")
      );
      document
        .getElementById("canvas" + (currentPage - 1) + "scaled")
        .parentElement.removeChild(
          document.getElementById("canvas" + (currentPage - 1) + "scaled")
        );
    }
    if (document.getElementById("canvas" + (currentPage + 1) + "scaled")) {
      removeScaledCanvasListener(
        document.getElementById("canvas" + (currentPage + 1) + "scaled")
      );
      document
        .getElementById("canvas" + (currentPage + 1) + "scaled")
        .parentElement.removeChild(
          document.getElementById("canvas" + (currentPage + 1) + "scaled")
        );
    }
    ifscaled = false;
  }
  if (isHandlingClick) {
    // 如果正在处理点击事件，则不执行任何操作
    return;
  }
  isHandlingClick = true;
  console.log(currentPage);

  await canvasDisplayController(currentPage);

  // 需要被节流
  batchLoadingCanvasPage(loadingPdf, currentPage).then(() => {
    console.log("batch loading end");
  });

  if (direction === "left") {
    removeCanvasChild(currentPage + 12);
  } else {
    removeCanvasChild(currentPage - 12);
  }
  callback();
};

// ==================== PDF Container Interaction Functions ====================

/**
 * Adds interaction listeners to the PDF container
 * @param {HTMLElement} pdfCanvas - The canvas element to add listeners to
 */
var addPdfContainerListener = async (pdfCanvas) => {
  const pdfContainer = document.getElementById("pdf-preview");
  let pageNum = parseInt(pdfCanvas.id.substring(6, pdfCanvas.id.length));
  console.log(parseInt(pdfCanvas.id.substring(6, pdfCanvas.id.length)));
  let page = await loadingPdf.then((value) =>
    value.getPage(pageNum).then(function (page) {
      console.log(1);
      return page;
    })
  );
  console.log(2);
  let isDragging = false;
  let startX, startY;
  let magnificationCanvas, magnificationContext;

  // 添加mousedown事件监听器
  pdfCanvas.addEventListener("mousedown", (e) => {
    isDragging = true;

    // 获取鼠标点击位置相对于PDF容器的坐标
    const rect = pdfCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;

    // 创建局部放大框的canvas
    magnificationCanvas = document.createElement("canvas");
    magnificationCanvas.classList.add("magnification-canvas");
    pdfContainer.appendChild(magnificationCanvas);

    magnificationCanvas.width = 200; // 你可以根据需要调整放大框的大小
    magnificationCanvas.height = 200;

    magnificationContext = magnificationCanvas.getContext("2d");

    // 设置初始位置
    updateMagnificationCanvas();
  });

  // 添加mousemove事件监听器
  pdfCanvas.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    // 获取鼠标当前位置相对于PDF容器的坐标
    const rect = pdfCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;

    // 更新局部放大框位置
    updateMagnificationCanvas();
  });

  // 添加mouseup事件监听器
  pdfCanvas.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;

      // 删除局部放大框的canvas
      pdfContainer.removeChild(magnificationCanvas);
    }
  });

  // 更新局部放大框的canvas位置
  function updateMagnificationCanvas() {
    const rectX = startX;
    const rectY = startY;

    magnificationCanvas.style.width = magnificationCanvas.width + "px";
    magnificationCanvas.style.height = magnificationCanvas.height + "px";
    magnificationCanvas.style.left = rectX + "px";
    magnificationCanvas.style.top = rectY + "px";

    // 渲染局部放大框的内容
    renderMagnificationContent(rectX, rectY);
  }

  // 渲染局部放大框的内容
  function renderMagnificationContent(x, y) {
    const ctx = magnificationContext;

    // 清空局部放大框
    ctx.clearRect(0, 0, magnificationCanvas.width, magnificationCanvas.height);

    // 将局部放大的部分绘制到局部放大框的canvas上
    //   drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight);
    ctx.drawImage(
      pdfCanvas,
      x,
      y,
      magnificationCanvas.width,
      magnificationCanvas.height,
      0,
      0,
      magnificationCanvas.width * 3,
      magnificationCanvas.height * 3
    );
  }

  // 添加样式
  const style = document.createElement("style");
  style.innerHTML = `
      .magnification-canvas {
        position: absolute;
        border: 2px solid red;
        pointer-events: none; /* 防止干扰鼠标事件 */
      }
    `;
  document.head.appendChild(style);
};

// ==================== Main PDF Display Function ====================

/**
 * Main function to display PDF
 */
var showPDF = () => {
  if (pdfObject.getPdf.type !== "application/pdf") {
    alert("请上传PDF文件");
    return;
  }
  batchLoadingCanvasPage(loadingPdf, pdfObject.getCurrentPage).then(() => {
    console.log("batch loading end");
    canvasDisplayController(pdfObject.getCurrentPage).then(() => {
      console.log("canvasDisplayController end");
    });
  });
};
