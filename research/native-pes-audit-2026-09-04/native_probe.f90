! Thin caller for the UNMODIFIED upstream 1AP PES, not a replacement potential.
! Read one (OO, OC, CO) distance triple in bohr and report raw energy/gradient.
program native_probe
  use callpot1
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  real(8) :: r(3), energy, grad(3)
  integer :: ios

  read(*, *, iostat=ios) r
  if (ios /= 0) stop 2
  call co21appes(r, energy, grad)
  write(*, '(A,4(1X,ES25.16E3))') 'RESULT', energy, grad
  write(*, '(A,4(1X,L1))') 'FINITE', ieee_is_finite(energy), ieee_is_finite(grad)
end program native_probe
