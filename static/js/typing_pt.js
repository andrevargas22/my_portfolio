// Array of words/phrases to display
const words = ["Eng. de Machine Learning", "Cientista de Dados", "pai de pet", "Marido da Maria", "gamer", "baterista", "aprendiz de xadrez", "web designer fake!"];

let i = 0; // Index variable to track current word/phrase
let timer; // Timer variable for setTimeout function

// Function to create typing effect
function typingEffect() {
    let word = words[i].split(""); 
    var loopTyping = function() { 
        if (word.length > 0) { 
            document.getElementById('word').innerHTML += word.shift(); 
        } else { 
            timer = setTimeout(deletingEffect, 1000); // Call the deletingEffect function after a delay of 1000ms (1 second)
            return false; 
        };
        timer = setTimeout(loopTyping, 50); // Call the loopTyping function recursively every 50ms to continue typing each character
    };
    loopTyping(); // Call the loopTyping function to start the typing effect
};

// Function to create deleting effect
function deletingEffect() {
    let word = words[i].split(""); 
    var loopDeleting = function() { 
        if (word.length > 0) { 
            word.pop(); 
            document.getElementById('word').innerHTML = word.join(""); // Update the HTML element with id 'word' to display the remaining characters as a string
        } else { // 
            if (words.length > (i + 1)) { 
                i++; 
            } else { 
                i = 0; // Reset the index variable to start from the beginning
            };
            typingEffect(); // Call the typingEffect function to start typing the next word/phrase
            return false; // Exit the loop
        };
        timer = setTimeout(loopDeleting, 25); // Call the loopDeleting function recursively every 25ms to continue deleting each character
    };
    loopDeleting(); // Call the loopDeleting function to start the deleting effect
};

typingEffect(); // Call the typingEffect function to start the typing animation when the script is first executed
