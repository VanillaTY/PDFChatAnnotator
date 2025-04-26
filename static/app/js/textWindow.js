/**
 * Text Window Module
 * Handles all text card related functionality including creation, submission and image management
 */

// ==================== Global Variables ====================
var draggingElement = null; // Currently dragged element
var responseBoxSelectedImgLists = []; // List of selected images for response boxes

// ==================== Image Management Functions ====================

/**
 * Adds images to a response box container
 * @param {HTMLElement} container - The container to add images to
 * @param {Array} imgLists - List of image sources to add
 */
var addResponseBoxImges = (container, imgLists) => {
  const imgClass = new SelectedImg();
  responseBoxSelectedImgLists.push(imgClass);

  let divLength = document.getElementsByClassName(
    "response-box-img-display-container"
  ).length;

  var imgDisplayBox = document.createElement("div");
  imgDisplayBox.classList.add("response-box-img-display-container");
  imgDisplayBox.id = "imgDisplayBox" + divLength;

  imgLists.forEach((imgSrc, index) => {
    var imgBox = document.createElement("div");
    imgBox.classList.add("response-box-img-box");
    imgBox.id = "divBox" + divLength + "-" + index;
    imgBox.containerId = imgDisplayBox.id;
    imgBox.imgClass = imgClass;

    var img = document.createElement("img");
    img.classList.add("response-box-img");
    img.src = submitCardImgRootPath + getFilenameFromPath(imgSrc);
    img.id = "image" + divLength + "-" + index;

    imgBox.appendChild(img);

    // Add delete icon
    var delIcon = document.createElement("img");
    delIcon.src = submitCardDelIcon;
    delIcon.classList.add("response-box-del-icon");
    delIcon.addEventListener("click", () => {
      delImageInSomeContainer(imgBox.id, imgBox.containerId, imgBox.imgClass);
    });
    imgBox.appendChild(delIcon);

    // Add tick icon
    var tickIcon = document.createElement("img");
    tickIcon.src = replaceFilenameInPath(submitCardTickIcon, "onTick.png");
    imgClass.addImg(getFilenameFromPath(img.src), img.id);
    tickIcon.classList.add("response-box-tick-icon");
    tickIcon.addEventListener("click", () => {
      tickImageInSomeContainer(imgBox.id, imgBox.containerId, imgBox.imgClass);
    });
    imgBox.appendChild(tickIcon);

    // Add drag and drop functionality
    imgBox.addEventListener("dragstart", function (event) {
      draggingElement = imgBox;
    });

    imgDisplayBox.appendChild(imgBox);
  });

  // Add drop zone functionality
  imgDisplayBox.addEventListener("dragover", function (event) {
    event.preventDefault();
  });
  imgDisplayBox.addEventListener("drop", function (event) {
    event.preventDefault();
    if (draggingElement) {
      updateDroppedElement(imgDisplayBox);
      draggingElement = null;
    }
  });

  container.appendChild(imgDisplayBox);
};

// ==================== Form Management Functions ====================

/**
 * Gets the current label values from a container
 * @param {HTMLElement} currentContainer - The container to get labels from
 * @returns {Object} Object containing label names and values
 */
var getCurrentLabelLists = (currentContainer) => {
  var labelLists = {};
  contentDiv = currentContainer.getElementsByClassName(
    "text-card-window-content"
  )[0];
  Array.from(
    contentDiv.getElementsByClassName("text-card-window-input-box")
  ).forEach((inputElement) => {
    let key = inputElement.querySelector("label").getAttribute("for");
    let value = inputElement.querySelector("input").value;
    labelLists[key] = value;
  });
  return labelLists;
};

/**
 * Creates and adds a new response box to the window
 * @param {Object} info - Information object containing label configurations
 * @param {Array} Images - List of images to add
 * @param {string} exampleText - Optional example text
 */
var addResponseBox = (info, Images, exampleText = "") => {
  console.log(info, Image, exampleText);
  // var info = {
  //     '名称': {'name': 'name', 'content': 'Name'},
  //     '时代': {'name': 'era', 'content': 'Era'},
  //     '出土地': {'name': 'discovery', 'content': 'Discovery'},
  //     '特征': {'name': 'feature', 'content': 'Feature'}
  // };
  // Create card container
  var card = document.createElement("card");
  card.classList.add("text-card");

  // Add avatar
  var avatar = document.createElement("div");
  avatar.classList.add("text-card-window-avatar");
  avatar.innerHTML = "It";
  avatar.addEventListener("click", () => {
    avatar.parentNode.remove();
  });
  card.appendChild(avatar);

  // Create content container
  var contentContainer = document.createElement("div");
  contentContainer.classList.add("text-card-window-container");

  // Add collect icon
  var collectIcon = document.createElement("img");
  collectIcon.classList.add("collect-icon");
  collectIcon.src = submitCardCollectIcon;
  collectIcon.addEventListener("click", function (event) {
    var imgIcon = getFilenameFromPath(this.src);
    let exampleText = this.parentElement
      .querySelector("form")
      .getElementsByClassName("exampleText")[0].value;
    if (imgIcon === "unstore.png") {
      this.src = replaceFilenameInPath(this.src, "store.png");
      examplePromptObject.addExample(
        this.parentElement.querySelector("form"),
        exampleText
      );
    } else {
      this.src = replaceFilenameInPath(this.src, "unstore.png");
      examplePromptObject.removeExample(
        this.parentElement.querySelector("form"),
        exampleText
      );
    }
  });
  contentContainer.appendChild(collectIcon);

  // Create form element
  var formElement = document.createElement("form");
  formElement.setAttribute("method", "post");
  formElement.classList.add("text-card-window-content");

  // Add example text input (hidden)
  var exampleInputElement = document.createElement("input");
  exampleInputElement.setAttribute("type", "text");
  exampleInputElement.setAttribute("name", "exampleText");
  exampleInputElement.setAttribute("class", "exampleText");
  exampleInputElement.value = exampleText;
  exampleInputElement.style.display = "none";
  formElement.appendChild(exampleInputElement);

  // Add input fields
  for (var key in info) {
    var inputBoxElement = document.createElement("div");
    inputBoxElement.classList.add("text-card-window-input-box");

    var labelElement = document.createElement("label");
    labelElement.innerHTML = key + "：";
    labelElement.setAttribute("for", info[key]["name"]);

    var inputElement = document.createElement("input");
    inputElement.setAttribute("type", "text");
    inputElement.setAttribute("name", info[key]["name"]);
    inputElement.setAttribute("id", info[key]["name"]);
    inputElement.value = info[key]["content"];

    inputBoxElement.appendChild(labelElement);
    inputBoxElement.appendChild(inputElement);

    var delIcon = document.createElement("img");
    delIcon.classList.add("input-del-icon");
    delIcon.src = submitCardInputDelIcon;
    delIcon.addEventListener("click", function (event) {
      this.parentElement.parentElement.removeChild(this.parentElement);
    });
    inputBoxElement.appendChild(delIcon);
    inputBoxElement.appendChild(document.createElement("br"));

    formElement.appendChild(inputBoxElement);
  }

  // Add input box addition functionality
  var addBoxElement = document.createElement("div");
  addBoxElement.classList.add("text-card-window-add-box");
  var addIcon = document.createElement("img");
  addIcon.classList.add("input-add-icon");
  addIcon.src = submitCardInputAddIcon;
  addIcon.addEventListener("click", function (event) {
    var inputElement = document.createElement("input");
    inputElement.classList.add("input-add-inputbox");
    inputElement.setAttribute("type", "text");
    addBoxElement.appendChild(inputElement);
    inputElement.focus();

    var yesIcon = document.createElement("img");
    yesIcon.classList.add("input-yes-icon");
    yesIcon.src = submitCardInputYesIcon;
    yesIcon.addEventListener("click", function (event) {
      let key = this.parentElement.querySelector("input").value;
      var inputBoxElement = document.createElement("div");
      inputBoxElement.classList.add("text-card-window-input-box");

      var labelElement = document.createElement("label");
      labelElement.innerHTML = key + "：";
      labelElement.setAttribute("for", key);

      var inputElement = document.createElement("input");
      inputElement.setAttribute("type", "text");
      inputElement.setAttribute("name", key);
      inputElement.setAttribute("id", key);
      inputElement.value = "";

      inputBoxElement.appendChild(labelElement);
      inputBoxElement.appendChild(inputElement);

      var delIcon = document.createElement("img");
      delIcon.classList.add("input-del-icon");
      delIcon.src = submitCardInputDelIcon;
      delIcon.addEventListener("click", function (event) {
        this.parentElement.parentElement.removeChild(this.parentElement);
      });
      inputBoxElement.appendChild(delIcon);
      inputBoxElement.appendChild(document.createElement("br"));

      formElement.insertBefore(inputBoxElement, this.parentElement);
      let parentNode = this.parentElement;
      Array.from(parentNode.children).forEach((ele) => {
        if (ele !== addIcon) {
          ele.parentElement.removeChild(ele);
        }
      });
      addIcon.style.display = "block";
    });
    addBoxElement.appendChild(yesIcon);

    var noIcon = document.createElement("img");
    noIcon.classList.add("input-no-icon");
    noIcon.src = submitCardInputNoIcon;
    noIcon.addEventListener("click", function (event) {
      let parentNode = this.parentElement;
      Array.from(parentNode.children).forEach((ele) => {
        if (ele !== addIcon) {
          ele.parentElement.removeChild(ele);
        }
      });
      addIcon.style.display = "block";
    });
    addBoxElement.appendChild(noIcon);
    addIcon.style.display = "none";
  });
  addBoxElement.appendChild(addIcon);
  formElement.appendChild(addBoxElement);

  // Add CSRF token
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const csrfInput = document.createElement("input");
  csrfInput.type = "hidden";
  csrfInput.name = "csrfmiddlewaretoken";
  csrfInput.value = csrfToken;
  formElement.appendChild(csrfInput);

  // Add submit button
  var submitButtonElement = document.createElement("input");
  submitButtonElement.setAttribute("type", "button");
  submitButtonElement.setAttribute("value", "Submit");
  submitButtonElement.setAttribute("id", "textCardSubmitBtn");
  submitButtonElement.addEventListener("click", function (event) {
    var divs = document.getElementsByClassName("text-card-window-container");
    var currentDiv = this.parentElement.parentElement;
    var index = Array.prototype.indexOf.call(divs, currentDiv);

    let imgLists = responseBoxSelectedImgLists[index].getSelectedImg;
    imgLists.forEach((val, index, array) => {
      array[index] = decodeURIComponent(val);
    });

    let labelLists = getCurrentLabelLists(currentDiv);
    onClickCardSubmitBtn(labelLists, imgLists, this);
  });
  formElement.appendChild(submitButtonElement);

  // Add form to container
  contentContainer.appendChild(formElement);
  card.appendChild(contentContainer);

  // Add card to window
  var window = document.getElementById("text-display");
  window.appendChild(card);

  // Add images
  addResponseBoxImges(contentContainer, Images);
};

// ==================== Text Input Functions ====================

/**
 * Calculates the width of text in a textarea
 * @param {HTMLTextAreaElement} textarea - The textarea element
 * @returns {number} The width of the text in pixels
 */
var computTextWidth = (textarea) => {
  var hiddenSpan = document.createElement("span");
  hiddenSpan.style.visibility = "hidden";
  hiddenSpan.style.whiteSpace = "nowrap";
  document.querySelector("body").appendChild(hiddenSpan);
  hiddenSpan.textContent = textarea.value;
  var textWidth = hiddenSpan.offsetWidth;
  document.querySelector("body").removeChild(hiddenSpan);
  return textWidth;
};

/**
 * Automatically resizes a textarea based on its content
 * @param {HTMLTextAreaElement} textarea - The textarea to resize
 */
var autoResize = (textarea) => {
  let valueLens = Math.max(computTextWidth(textarea), 20);
  textarea.style.width = valueLens + "px";
};

// ==================== Tag Management Functions ====================

/**
 * Removes a tag from the tag box
 * @param {HTMLElement} tagIcon - The tag icon element
 */
function removeTag(tagIcon) {
  tagIcon.parentElement.parentElement.removeChild(tagIcon.parentElement);
}

/**
 * Adds a new tag to the tag box
 */
var addTag = () => {
  var father = document.querySelector(".text-send-message-tag-box");
  var tag = document.createElement("div");
  tag.classList.add("text-send-message-tag");

  var textarea = document.createElement("textarea");
  textarea.addEventListener("input", function () {
    autoResize(this);
  });

  var iconImg = document.createElement("img");
  iconImg.src = inputTagDelIcon;
  iconImg.classList.add("tag-del");
  iconImg.addEventListener("click", function () {
    removeTag(this);
  });

  tag.appendChild(textarea);
  tag.appendChild(iconImg);
  father.appendChild(tag);
};

/**
 * Handles click event for adding a new tag
 */
var onClickAddTagIcon = () => {
  addTag();
};

// ==================== Chat Container Functions ====================

/**
 * Adjusts the height of the chat container based on content
 */
function adjustChatContainerHeight() {
  const chatContainer = document.getElementsByClassName(
    "text-send-message-box"
  )[0];
  const messageInput = document.getElementsByClassName(
    "text-send-message-box-input-field"
  )[0];

  chatContainer.style.height = "auto";
  messageInput.style.height = "auto";

  const computedStyle = window.getComputedStyle(messageInput);
  const messageInputPaddingTop = computedStyle.getPropertyValue("padding-top");

  const scrollHeight =
    messageInput.scrollHeight - parseInt(messageInputPaddingTop) * 2;
  const maxContainerHeight = parseInt(
    getComputedStyle(chatContainer).maxHeight
  );

  chatContainer.style.height =
    Math.min(
      scrollHeight + parseInt(messageInputPaddingTop) * 2,
      maxContainerHeight
    ) + "px";
  messageInput.style.height = Math.min(scrollHeight) + "px";
}

// ==================== Card Submission Functions ====================

/**
 * Handles the card submission process
 * @param {Object} labelLists - Object containing label names and values
 * @param {Array} ImgLists - List of images to submit
 * @param {HTMLElement} submitButton - The submit button element that was clicked
 */
var onClickCardSubmitBtn = (labelLists, ImgLists, submitButton) => {
  submitButton.disabled = true;
  submitButton.value = "Saving...";

  $.ajax({
    url: submitCardUrl,
    type: "post",
    data: {
      labelLists: JSON.stringify(labelLists),
      ImgLists: ImgLists,
    },
  })
    .done(function (response) {
      const json =
        typeof response === "string" ? JSON.parse(response) : response;

      if (json.status) {
        submitButton.value = "Saved";
        submitButton.style.backgroundColor = "#4CAF50";
        submitButton.style.cursor = "not-allowed";

        // Clear selected images
        selectedImgLists.getSelectedImgId.forEach((id) => {
          delImageByFullId(document.getElementById(id).parentElement.id);
        });
        selectedImgLists.dumpImg();
      } else {
        submitButton.disabled = false;
        submitButton.value = "Save Failed";
        submitButton.style.backgroundColor = "#f44336";
        setTimeout(() => {
          submitButton.value = "Submit";
          submitButton.style.backgroundColor = "";
        }, 3000);
      }
    })
    .fail(function () {
      submitButton.disabled = false;
      submitButton.value = "Save Failed";
      submitButton.style.backgroundColor = "#f44336";
      setTimeout(() => {
        submitButton.value = "Submit";
        submitButton.style.backgroundColor = "";
      }, 3000);
    });
};
