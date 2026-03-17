let A = 20
let B = 40
let C = A + B * B

try
    let D = C / 0
catch
    display "Error: Division by zero attempted but not allowed."
end

display "The result is "
display C