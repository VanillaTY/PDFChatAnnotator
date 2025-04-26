/**
 * Main Application Scripts
 * Handles PDF management, image selection, and UI interactions
 */

// ==================== Class Definitions ====================

/**
 * PDF Management Class
 * Handles PDF file state and page management
 */
class pdf {
  constructor() {
    this.currentPage = 1;
    this.pdf = null;
    this.pdfLength = 0;
  }
  // js中get set关键字可以在设置属性值时，可以像设置普通属性一样使用赋值运算符
  get getCurrentPage() {
    return this.currentPage;
  }
  get getPdf() {
    return this.pdf;
  }
  get getPdfLength() {
    return this.pdfLength;
  }
  set setCurrentPage(pageNum) {
    this.currentPage = pageNum;
  }
  set setPdf(pdfObject) {
    this.pdf = pdfObject;
  }
  set setPdfLength(pdfLength) {
    this.pdfLength = pdfLength;
  }
}

/**
 * Image Selection Management Class
 * Handles selected images state and operations
 */
class SelectedImg {
  constructor() {
    this.imgLists = [];
    this.imgId = [];
  }
  // js中get set关键字可以在设置属性值时，可以像设置普通属性一样使用赋值运算符
  get getSelectedImg() {
    return this.imgLists;
  }
  get getSelectedImgId() {
    return this.imgId;
  }
  set setSelectedImg(selectedImgLists_new) {
    this.imgLists = selectedImgLists_new;
  }
  /**
   * Adds a new image to the selection
   * @param {string} img_new - The image source
   * @param {string} img_new_id - The image ID
   */
  addImg(img_new, img_new_id) {
    this.imgId.push(img_new_id);
    this.imgLists.push(img_new);
    console.log(this.getSelectedImg, this.getSelectedImgId);
  }
  /**
   * Removes an image from the selection
   * @param {string} imgName - The image source to remove
   * @param {string} imgId - The image ID to remove
   * @returns {Array} The updated image list
   */
  removeImg(imgName, imgId) {
    var index = this.imgLists.indexOf(imgName); // 查找要删除的元素的索引
    var indexId = this.imgId.indexOf(imgId);
    if (index > -1) {
      this.imgLists.splice(index, 1); // 从数组中删除指定索引位置的元素
      this.imgId.splice(indexId, 1);
    }
    console.log(this.getSelectedImg, this.getSelectedImgId);
    return this.imgLists;
  }
  /**
   * Clears all selected images
   */
  dumpImg() {
    this.imgLists = [];
    this.imgId = [];
  }
}

// ==================== Global Variables ====================

// PDF and image management instances
const pdfObject = new pdf();
const selectedImgLists = new SelectedImg();

// Response box image lists
var responseBoxSelectedImgLists = [];

// UI state variables
var isHandlingClick = false;
var loadingPdf = null;

// ==================== Event Handlers ====================

/**
 * Initializes the application when the document is ready
 */
$(document).ready(function () {
  addFormListner();

  const inputPDF = document.getElementById("file");

  inputPDF.addEventListener("change", function (event) {
    pdfObject.setPdf = event.target.files[0];
    pdfObject.setCurrentPage = 1;
    try {
      // showPDF();
      (async () => {
        loadingPdf = (async () => await loadingPDF())();
        await loadingPdf;
        showPDF();
      })();
    } catch (error) {
      console.error("LoadingPDF Error:", error);
    }
  });

  const leftPageBtn = document.getElementById("pdf-pageNum-left-btn");
  leftPageBtn.addEventListener("click", function (event) {
    if (isHandlingClick) {
      // 如果正在处理点击事件，则不执行任何操作
      return;
    }
    // 设置标志表示正在处理点击事件
    // isHandlingClick = true;

    pdfObject.setCurrentPage = pdfObject.getCurrentPage - 1;

    changePDFPage(loadingPdf, "left", pdfObject.getCurrentPage, function () {
      isHandlingClick = false;
    });
    // showPDF(pdfObject.getPdf, pdfObject.getCurrentPage);
  });
  const rightPageBtn = document.getElementById("pdf-pageNum-right-btn");
  rightPageBtn.addEventListener("click", function (event) {
    if (isHandlingClick) {
      // 如果正在处理点击事件，则不执行任何操作
      return;
    }
    // 设置标志表示正在处理点击事件
    // isHandlingClick = true;
    pdfObject.setCurrentPage = pdfObject.getCurrentPage + 1;

    changePDFPage(loadingPdf, "right", pdfObject.getCurrentPage, function () {
      isHandlingClick = false;
    });
    // showPDF(pdfObject.getPdf, pdfObject.getCurrentPage);
  });

  const pageNumInput = document.getElementById("pdf-pageNum-current");
  pageNumInput.addEventListener("blur", function (event) {
    if (pageNumInput.value) {
      pdfObject.setCurrentPage = parseInt(pageNumInput.value);
    }
    showPDF();
  });

  // 用于测试
  let info = {
    名称: { name: "name", content: "Name" },
    时代: { name: "era", content: "Era" },
    出土地: { name: "discovery", content: "Discovery" },
    特征: { name: "feature", content: "Feature" },
  };
  let tmp = [
    "app/loadedImgs/pageNumber37_147.png",
    "app/loadedImgs/pageNumber37_149.png",
    "app/loadedImgs/pageNumber37_147.png",
    "app/loadedImgs/pageNumber37_149.png",
    "app/loadedImgs/pageNumber37_147.png",
    "app/loadedImgs/pageNumber37_149.png",
  ];
  // addResponseBox(info, tmp)
  // addResponseBox(info, tmp)
  const messageSendBtn = document.querySelector(
    ".text-send-message-send-button"
  );
  messageSendBtn.addEventListener("click", (event) => {
    onClickMessageSendBtn();
    // event.preventDefault();
  });
});
