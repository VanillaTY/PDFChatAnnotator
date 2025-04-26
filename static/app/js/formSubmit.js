/**
 * Form Submission Module
 * Handles form submission, file upload, and form event listeners
 */

// ==================== Form Submission Functions ====================

/**
 * Handles the file submission process
 * Sends the file and related data to the server
 */
var onClickFileHandleBtn = () => {
  console.log("FileSend");
  // 创建一个 FormData 对象
  var formData = new FormData();

  const filename = document.querySelector(
    "#form-container-file-name-display"
  ).innerHTML;
  if (filename === "") {
    alert("Please upload a PDF!");
    return;
  }

  const file = document.querySelector("#file").files[0];

  const pageNum = document.querySelector("#pdf-pageNum-current").value;
  const pageLength = document.querySelector("#file-space-pdf-length").value;
  const lang = `${document.querySelector("#langSelect").value},en`;

  formData.append("file", file);
  formData.append("filename", filename);
  formData.append("pageNum", pageNum);
  formData.append("pageLength", pageLength);
  formData.append("lang", lang);

  const loader_icon = document.querySelector(".loader");
  loader_icon.style.display = "block";

  $.ajax({
    url: fileHandleUrl,
    type: "post",
    data: formData,
    processData: false, // 不处理数据
    contentType: false, // 不设置内容类型
  })
    .done(function (json) {
      console.log(json);
      loader_icon.style.display = "none";
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      console.log("Request error:", errorThrown);
      // 在这里处理请求失败的情况
      loader_icon.style.display = "none";
    });
};

// ==================== Form Event Listeners ====================

/**
 * Sets up form event listeners and handlers
 * Initializes file upload and form submission functionality
 */
var addFormListner = () => {
  // 获取表单元素和按钮元素
  const form1 = document.querySelector("#fileForm");
  const form2 = document.querySelector("#askListForm");
  const askMessageSendBox = document.querySelector(
    ".text-send-message-box-input-field"
  );
  const pageNum = document.querySelector("#pdf-pageNum-current");
  const submitBtn = form1.querySelector("button[type=submit]");

  const formContainer = document.querySelector(".form-container");
  const formFileInput = document.querySelector("#file");
  formContainer.addEventListener("click", (event) => {
    formFileInput.click();
  });
  formFileInput.addEventListener("change", (event) => {
    var files = event.target.files;
    if (files.length > 0) {
      var fileName = files[0].name;
      document.getElementById("form-container-file-upload-icon").style.display =
        "none";
      document.getElementById(
        "form-container-file-name-display"
      ).style.display = "block";
      document.getElementById("form-container-file-name-display").textContent =
        fileName;
    }
  });
};
