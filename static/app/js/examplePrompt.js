/**
 * Example Prompt Management Module
 * Handles example prompts collection and management for the application
 */

/**
 * Example Prompt Management Class
 * Manages a collection of example prompts and their associated elements
 */
class examplePrompt {
  constructor() {
    this.examples = [];
  }
  // js中get set关键字可以在设置属性值时，可以像设置普通属性一样使用赋值运算符
  get getExamples() {
    let allPrompts = "";
    this.examples.forEach((data) => {
      let text = data.example;
      let answer =
        "Answer: " +
        JSON.stringify(getCurrentLabelLists(data.element.parentElement));
      let prompt = "Example: " + text + answer;
      allPrompts = allPrompts + prompt;
    });
    return allPrompts;
  }
  addExample(element, example) {
    this.examples.push({
      element: element,
      example: example,
    });
    if (this.examples.length > 3) {
      this.examples[0].element.parentElement
        .getElementsByClassName("collect-icon")[0]
        .click();
    }
    console.log(this.examples);
  }
  removeExample(element, example) {
    this.examples = this.examples.filter((item) => item.element !== element);
    console.log(this.examples);
  }
}
const examplePromptObject = new examplePrompt();
