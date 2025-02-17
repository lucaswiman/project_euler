% Each new term in the Fibonacci sequence is generated by adding the previous two terms. By starting with 1 and 2, the first 10 terms will be:
%
% 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
%
% By considering the terms in the Fibonacci sequence whose values do not exceed four million, find the sum of the even-valued terms.

:- dynamic
  fib/2
.

fib(N, 1) :-
  N < 2
.

fib(N, Fib) :-
  succ(A, N), fib(A, Fib1),
  succ(B, A), fib(B, Fib2),
  Fib is Fib1 + Fib2,
  asserta(fib(N, Fib) :- !)
.

applicable(Fib, Max) :-
  0 is Fib mod 2,
  Fib < Max
.

problem2_helper(N, Acc, Max, Solution) :-
  fib(N, Fib),
  % writeln([N, Acc]),
  (
    (not(applicable(Fib, Max)), Solution is Acc);
    % Not assigning N+3 to a variable yields the following vexing error:
    % ERROR: succ/2: Type error: `integer' expected, found `2+3'
    (Wtf is N+3, problem2_helper(Wtf, Acc+Fib, Max, Solution))
  )
.

problem2(Max, Solution) :-
  problem2_helper(2, 0, Max, Solution)
.

:- initialization problem2(4000000, Solution), writeln(Solution), halt.
