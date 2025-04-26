/**
 * Image Display Management Module
 * Handles image display, selection, and drag-and-drop functionality
 */

// ==================== Utility Functions ====================

/**
 * Extracts filename from a file path
 * @param {string} filePath - The full file path
 * @returns {string} The filename extracted from the path
 */
function getFilenameFromPath(filePath) {
  var parts = filePath.split(/[\\/]/);
  var filename = parts.pop();
  return filename;
}

/**
 * Replaces filename in a file path with a new filename
 * @param {string} filePath - The original file path
 * @param {string} newFilename - The new filename to use
 * @returns {string} The updated file path
 */
function replaceFilenameInPath(filePath, newFilename) {
  var parts = filePath.split(/[\\/]/);
  parts.pop(); // 移除最后一部分（文件名）
  parts.push(newFilename); // 添加新的文件名
  var newPath = parts.join("/");
  return newPath;
}

// ==================== Image Container Management ====================

/**
 * Removes an image from a specific container
 * @param {string} imgId - The ID of the image to remove
 * @param {string} containerId - The ID of the container
 * @param {Object} imgClass - The image class instance managing the selection
 */
var delImageInSomeContainer = (imgId, containerId, imgClass) => {
  var imgDisplay = document.getElementById(containerId);
  var imgBox = document.getElementById(imgId);
  var imgBoxIcon = getFilenameFromPath(imgBox.children[2].src);
  if (imgBoxIcon == "onTick.png") {
    imgClass.removeImg(
      getFilenameFromPath(imgBox.children[0].src),
      imgBox.children[0].id
    );
  }
  imgDisplay.removeChild(imgBox);
};

/**
 * Removes an image by its full ID from the main image display
 * @param {string} imgId - The ID of the image to remove
 */
var delImageByFullId = (imgId) => {
  var imgDisplay = document.getElementById("image-display");
  var imgBox = document.getElementById(imgId);
  imgDisplay.removeChild(imgBox);
};

// ==================== Image Selection Management ====================

/**
 * Toggles the selection state of an image in a container
 * @param {string} imgId - The ID of the image to toggle
 * @param {string} containerId - The ID of the container
 * @param {Object} imgClass - The image class instance managing the selection
 */
var tickImageInSomeContainer = (imgId, containerId, imgClass) => {
  var imgDisplay = document.getElementById(containerId);
  var imgBox = document.getElementById(imgId);
  var imgIcon = getFilenameFromPath(imgBox.children[2].src);
  if (imgIcon == "tick.png") {
    //点击
    let newImgIcon = replaceFilenameInPath(
      imgBox.children[2].src,
      "onTick.png"
    );
    imgBox.children[2].src = newImgIcon;
    imgClass.addImg(
      getFilenameFromPath(imgBox.children[0].src),
      imgBox.children[0].id
    );
  } else {
    let newImgIcon = replaceFilenameInPath(imgBox.children[2].src, "tick.png");
    imgBox.children[2].src = newImgIcon;
    imgClass.removeImg(
      getFilenameFromPath(imgBox.children[0].src),
      imgBox.children[0].id
    );
  }
  // imgDisplay.removeChild(imgBox);
};

// ==================== Drag and Drop Management ====================

/**
 * Updates the state of a dragged element after being dropped
 * @param {HTMLElement} imgDisplayBox - The container where the element was dropped
 */
var updateDroppedElement = (imgDisplayBox) => {
  var draggingElementIcon = getFilenameFromPath(
    draggingElement.children[2].src
  );
  let previousId = draggingElement.children[0].id;
  let previousImgSource = draggingElement.children[0].src;
  let previousImgClass = draggingElement.imgClass;

  //更新 containerId
  draggingElement.containerId = imgDisplayBox.id;

  //加到新的容器中
  imgDisplayBox.appendChild(draggingElement);

  //更新imgClass
  var divs = document.getElementsByClassName("text-card-window-container");
  var currentDiv = draggingElement.parentElement.parentElement;
  var index = Array.prototype.indexOf.call(divs, currentDiv); // 获取当前 <div> 在数组中的索引位置
  let imgClass = responseBoxSelectedImgLists[index];
  draggingElement.imgClass = imgClass;

  if (draggingElementIcon == "tick.png") {
    //之前是未选中状态
    //到新的容器中变为选中状态
    tickImageInSomeContainer(
      draggingElement.id,
      draggingElement.containerId,
      imgClass
    );
  } else {
    //之前是选中状态
    //从之前ImgClass中删除
    previousImgClass.removeImg(
      getFilenameFromPath(previousImgSource),
      previousId
    );
    //加到新到ImgClass中
    imgClass.addImg(
      getFilenameFromPath(draggingElement.children[0].src),
      draggingElement.children[0].id
    );
  }

  console.log(previousImgClass, imgClass);
};
