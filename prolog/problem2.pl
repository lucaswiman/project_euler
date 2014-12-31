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


% http://rosettacode.org/wiki/Fibonacci_sequence#With_lazy_lists_3
fib_lazy([0,1|X]) :-
  fib_lazy_helper(0,1,X)
.

fib_lazy_helper(A,B,X) :-
  freeze(X, (C is A+B, X=[C|Y], fib_lazy_helper(B,C,Y)))
.

sum_list([], []).
sum_list([Elem|List], [Elem|Sums]) :-
  sum_list_helper(Elem, List, Sums)
.
sum_list_helper(_, [], []).
sum_list_helper(Acc, [Elem|List], Sums) :-
  freeze(Sums, (
      NextAcc is Acc + Elem,
      Sums = [NextAcc|NextSums],
      sum_list_helper(NextAcc, List, NextSums)
    )
  )
.
