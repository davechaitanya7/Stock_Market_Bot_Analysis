class Calculator {
  constructor() {
    this.currentOperand = '0';
    this.previousOperand = '';
    this.operation = undefined;
    this.shouldResetScreen = false;

    this.currentOperandElement = document.getElementById('currentOperand');
    this.previousOperandElement = document.getElementById('previousOperand');

    this.init();
  }

  init() {
    document.querySelectorAll('.btn').forEach(button => {
      button.addEventListener('click', () => this.handleButton(button));
    });

    document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    this.updateDisplay();
  }

  handleButton(button) {
    const value = button.dataset.value;
    const action = button.dataset.action;

    if (value) {
      this.appendNumber(value);
    } else if (action) {
      this.handleAction(action);
    }

    this.updateDisplay();
  }

  handleKeyboard(e) {
    if (e.key >= '0' && e.key <= '9') this.appendNumber(e.key);
    if (e.key === '.') this.appendNumber('.');
    if (e.key === '+' || e.key === '-') this.handleAction(e.key === '+' ? 'add' : 'subtract');
    if (e.key === '*') this.handleAction('multiply');
    if (e.key === '/') {
      e.preventDefault();
      this.handleAction('divide');
    }
    if (e.key === 'Enter' || e.key === '=') {
      e.preventDefault();
      this.calculate();
    }
    if (e.key === 'Backspace') this.delete();
    if (e.key === 'Escape') this.clear();
    if (e.key === '%') this.handleAction('percent');

    this.updateDisplay();
  }

  appendNumber(num) {
    if (num === '.' && this.currentOperand.includes('.')) return;
    if (this.shouldResetScreen) {
      this.currentOperand = num === '.' ? '0.' : num;
      this.shouldResetScreen = false;
    } else {
      this.currentOperand = this.currentOperand === '0' && num !== '.'
        ? num
        : this.currentOperand + num;
    }
  }

  handleAction(action) {
    switch (action) {
      case 'clear':
        this.clear();
        break;
      case 'delete':
        this.delete();
        break;
      case 'add':
      case 'subtract':
      case 'multiply':
      case 'divide':
        this.setOperation(action);
        break;
      case 'calculate':
        this.calculate();
        break;
      case 'percent':
        this.percent();
        break;
      case 'sqrt':
        this.squareRoot();
        break;
    }
  }

  clear() {
    this.currentOperand = '0';
    this.previousOperand = '';
    this.operation = undefined;
  }

  delete() {
    this.currentOperand = this.currentOperand.slice(0, -1) || '0';
  }

  setOperation(op) {
    if (this.previousOperand !== '') {
      this.calculate();
    }
    this.operation = op;
    this.previousOperand = this.currentOperand;
    this.currentOperand = '0';
  }

  calculate() {
    if (!this.operation || this.previousOperand === '') return;

    const prev = parseFloat(this.previousOperand);
    const current = parseFloat(this.currentOperand);
    if (isNaN(prev) || isNaN(current)) return;

    let result;
    switch (this.operation) {
      case 'add':
        result = prev + current;
        break;
      case 'subtract':
        result = prev - current;
        break;
      case 'multiply':
        result = prev * current;
        break;
      case 'divide':
        result = current !== 0 ? prev / current : 'Error';
        break;
    }

    this.currentOperand = this.formatResult(result);
    this.operation = undefined;
    this.previousOperand = '';
    this.shouldResetScreen = true;
  }

  percent() {
    this.currentOperand = this.formatResult(parseFloat(this.currentOperand) / 100);
    this.shouldResetScreen = true;
  }

  squareRoot() {
    const current = parseFloat(this.currentOperand);
    if (current < 0) {
      this.currentOperand = 'Error';
    } else {
      this.currentOperand = this.formatResult(Math.sqrt(current));
    }
    this.shouldResetScreen = true;
  }

  formatResult(result) {
    if (result === 'Error') return 'Error';
    const str = result.toString();
    if (str.length > 12) {
      return result.toPrecision(10).replace(/\.?0+$/, '');
    }
    return str;
  }

  updateDisplay() {
    this.currentOperandElement.textContent = this.formatDisplay(this.currentOperand);
    this.previousOperandElement.textContent = this.previousOperand
      ? `${this.formatDisplay(this.previousOperand)} ${this.getOperatorSymbol()}`
      : '';
  }

  formatDisplay(num) {
    if (num === 'Error') return num;
    const parts = num.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.join('.');
  }

  getOperatorSymbol() {
    const symbols = { add: '+', subtract: '−', multiply: '×', divide: '÷' };
    return symbols[this.operation] || '';
  }
}

document.addEventListener('DOMContentLoaded', () => new Calculator());
