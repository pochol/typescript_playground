// validation logic
interface Validateble {
  value: string | number;
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
}

function validate(validatebleInput: Validateble): boolean {
  let isValid = true;
  if (validatebleInput.required) {
    isValid = isValid && validatebleInput.value.toString().trim().length !== 0;
  }
  if (
    validatebleInput.minLength != null &&
    typeof validatebleInput.value === "string"
  ) {
    isValid =
      isValid && validatebleInput.value.length >= validatebleInput.minLength;
  }

  if (
    validatebleInput.maxLength != null &&
    typeof validatebleInput.value === "string"
  ) {
    isValid =
      isValid && validatebleInput.value.length <= validatebleInput.maxLength;
  }

  if (
    validatebleInput.min != null &&
    typeof validatebleInput.value === "number"
  ) {
    isValid = isValid && validatebleInput.value >= validatebleInput.min;
  }
  if (
    validatebleInput.max != null &&
    typeof validatebleInput.value === "number"
  ) {
    isValid = isValid && validatebleInput.value <= validatebleInput.max;
  }
  return isValid;
}

// autobind decoration6
function Autobind(_: any, _2: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const adjustDescriptor: PropertyDescriptor = {
    configurable: true,
    get() {
      const boundFunction = originalMethod.bind(this);
      return boundFunction;
    },
  };
  return adjustDescriptor;
}
// ProjectInput class
class ProjectInput {
  templeElement: HTMLTemplateElement;
  hostElement: HTMLDivElement;
  element: HTMLFormElement;
  titleInputElement: HTMLInputElement;
  // @Required // decorator
  descriptionInputElement: HTMLInputElement;
  // @Required
  peopleInputElement: HTMLInputElement;
  // @Required
  projetList: HTMLTemplateElement;

  constructor() {
    this.templeElement = <HTMLTemplateElement>(
      document.getElementById("project-input")!
    );
    this.hostElement = <HTMLDivElement>document.getElementById("app")!;

    const importedNode = document.importNode(this.templeElement.content, true);
    this.element = importedNode.firstElementChild as HTMLFormElement;
    this.element.id = "user-input";
    this.titleInputElement = this.element.querySelector(
      "#title"
    )! as HTMLInputElement;
    this.descriptionInputElement = this.element.querySelector(
      "#description"
    )! as HTMLInputElement;
    this.peopleInputElement = this.element.querySelector(
      "#people"
    )! as HTMLInputElement;

    this.projetList = document.getElementById(
      "project-list"
    ) as HTMLTemplateElement;
    this.configure();
    this.attach();
  }

  private gatherUserInput(): [string, string, number] | void {
    const enteredTitle = this.titleInputElement.value;
    const enteredDescription = this.descriptionInputElement.value;
    const enteredPeople = this.peopleInputElement.value;

    const titleValidateble: Validateble = {
      value: enteredTitle,
      required: true,
    };
    const descriptionValidateble: Validateble = {
      value: enteredDescription,
      required: true,
      minLength: 5,
    };
    const peopleValidateble: Validateble = {
      value: +enteredPeople,
      required: true,
      min: 1,
      max: 5,
    };

    if (
      !validate(titleValidateble) ||
      !validate(descriptionValidateble) ||
      !validate(peopleValidateble)
    ) {
      console.log("Invalid input, please try again");
    } else {
      return [enteredTitle, enteredDescription, +enteredPeople];
    }
  }

  private clearInputs(): void {
    this.titleInputElement.value = "";
    this.descriptionInputElement.value = "";
    this.peopleInputElement.value = "";
  }

  // decorator in action
  @Autobind
  private submitHandler(event: Event): void {
    event.preventDefault();
    const userInput = this.gatherUserInput();

    if (Array.isArray(userInput)) {
      const [title, desc, people] = userInput;
      console.log(title, desc, people);
      this.clearInputs();
    }
  }

  private configure(): void {
    this.element.addEventListener("submit", this.submitHandler);
  }

  private attach(): void {
    this.hostElement.insertAdjacentElement("afterbegin", this.element);
  }
}

const projectInput = new ProjectInput();
