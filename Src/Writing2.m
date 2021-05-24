function [P1,X,Y,Z,P11] = Writing2()

Track = load('result');

P1 = Track(1, 1:3);
P11 = Track(2, 1:3);
X = Track(3, :);
Y = Track(4, :);
Z = Track(5, :);

end

