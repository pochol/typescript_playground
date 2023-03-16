// required decorator
// function Required(
//   _: any,
//   _2: string,
//   descriptor: PropertyDescriptor
// ) {

// }


// autobind decoration6
function Autobind(
  _: any,
  _2: string,
  descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const adjustDescriptor: PropertyDescriptor = {
    configurable: true,
    get() {
      const boundFunction = originalMethod.bind(this);
      return boundFunction;
    }
  }
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

    this.projetList = document.getElementById('project-list') as HTMLTemplateElement;
    this.configure();
    this.attach();
  }

  private gatherUserInput(): [string, string, number] | void {
    const enteredTitle = this.titleInputElement.value;
    const enteredDescription = this.descriptionInputElement.value;
    const enteredPeople = this.peopleInputElement.value;

    if(
      enteredTitle.trim().length === 0 ||
      enteredDescription.trim().length === 0 ||
      enteredPeople.trim().length === 0
    ) {
      console.log('Invalid input, please try again')
    } else {
      return [enteredTitle, enteredDescription, +enteredPeople];
    }
  }

  // decorator in action
  @Autobind
  private submitHandler(event: Event) {
    event.preventDefault();
    const userInput = this.gatherUserInput();
    console.log(userInput);
  }

  private configure() {
    this.element.addEventListener('submit', this.submitHandler);
  }

  private attach() {
    this.hostElement.insertAdjacentElement("afterbegin", this.element);
  }
}

const projectInput = new ProjectInput();
