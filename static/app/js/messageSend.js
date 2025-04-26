/**
 * Message Sending Module
 * Handles message sending functionality and response display
 */

// ==================== Message Sending Functions ====================

/**
 * Handles the click event of the message send button
 * Sends the message to the server and processes the response
 */
var onClickMessageSendBtn = () => {
  // Get message input and clear the input field
  let message = document.getElementsByClassName(
    "text-send-message-box-input-field"
  )[0].value;
  if (!message.trim()) return; // 如果消息为空，直接返回

  document.getElementsByClassName(
    "text-send-message-box-input-field"
  )[0].value = "";

  // Adjust chat container height
  adjustChatContainerHeight();

  // Get PDF information
  const pageNum = document.querySelector("#pdf-pageNum-current").value;
  const pageLength = document.querySelector("#file-space-pdf-length").value;
  const filename = document.querySelector(
    "#form-container-file-name-display"
  ).innerHTML;

  // Validate PDF upload
  if (filename === "") {
    showError("请先上传PDF文件！");
    return;
  }

  // Add message to chat display
  addMessageAskBox(message);

  // Show loading state
  const loadingIndicator = document.createElement("div");
  loadingIndicator.className = "loading-indicator";
  loadingIndicator.innerHTML =
    '<div class="spinner"></div><span>正在处理...</span>';
  document.getElementById("text-display").appendChild(loadingIndicator);

  // Get example prompts
  let prompts = examplePromptObject.getExamples;

  // Send AJAX request to server
  $.ajax({
    url: receiveMessageUrl,
    type: "post",
    data: {
      message: message,
      pageNum: pageNum,
      pageLength: pageLength,
      filename: filename,
      prompt: examplePromptObject.getExamples,
    },
    timeout: 30000, // 设置超时时间为30秒
  })
    .done(function (json) {
      try {
        console.log("respnse json", json);
        // Process server response
        var data = JSON.parse(json);
        if (!data.status) {
          throw new Error(data.error || "处理失败");
        }

        let modelOutputs = data.modelOutputs;
        let exampleTextList = data.exampleTextList;
        let imgLists = data.imgList;
        console.log("modelOutputs", modelOutputs);
        // Process each model output
        modelOutputs.forEach((modelOutput, index) => {
          let imgList = imgLists[index];
          console.log("modelOutput", index);
          // Convert model output to info object
          let info = {};
          for (let key in modelOutput) {
            info[key] = { name: key, content: modelOutput[key] };
          }

          // Add response box with info and images
          addResponseBox(info, imgList, exampleTextList[index]);
        });
      } catch (error) {
        showError("处理响应时出错: " + error.message);
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      showError(
        "请求失败: " + (textStatus === "timeout" ? "请求超时" : errorThrown)
      );
    })
    .always(function () {
      // Remove loading indicator
      loadingIndicator.remove();
    });
};

/**
 * Shows an error message in the chat
 * @param {string} message - The error message to display
 */
function showError(message) {
  const errorBox = document.createElement("div");
  errorBox.className = "error-message";
  errorBox.textContent = message;
  document.getElementById("text-display").appendChild(errorBox);

  // Auto remove after 5 seconds
  setTimeout(() => {
    errorBox.remove();
  }, 5000);
}

// ==================== UI Management Functions ====================

/**
 * Adds a message ask box to the chat display
 * @param {string} message - The message text to display
 */
var addMessageAskBox = (message) => {
  // Create message container
  var textAskWindow = document.createElement("div");
  textAskWindow.className = "text-ask-window";

  // Create content container
  var textAskWindowContent = document.createElement("div");
  textAskWindowContent.className = "text-ask-window-content";

  // Create message text element
  var textAskWindowHint = document.createElement("div");
  textAskWindowHint.className = "text-ask-window-hint";
  textAskWindowHint.textContent = message;

  // Create avatar element with delete functionality
  var textAskWindowAvatar = document.createElement("div");
  textAskWindowAvatar.className = "text-ask-window-avatar";
  textAskWindowAvatar.textContent = "Me";
  textAskWindowAvatar.addEventListener("click", () => {
    textAskWindowAvatar.parentNode.remove();
  });

  // Assemble the message box
  textAskWindowContent.appendChild(textAskWindowHint);
  textAskWindow.appendChild(textAskWindowContent);
  textAskWindow.appendChild(textAskWindowAvatar);

  // Add to chat display
  document.getElementById("text-display").appendChild(textAskWindow);
};
