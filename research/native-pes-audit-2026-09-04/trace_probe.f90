! Diagnostic caller only: upstream routines and data are unchanged.
program trace_probe
  use callpot1
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  real(8) :: r(3), rr(3), mm(3), xp(3), v, grad(3), capr, theta, deriv(3,3)
  real(8), parameter :: mo = 15.99491462d0, mc = 12d0
  integer :: ios, arrangement, axis, offset
  read(*,*,iostat=ios) r
  if (ios /= 0) stop 2
  do arrangement = 1, 3
    select case (arrangement)
    case (1)
      rr = [r(1), r(3), r(2)]
      mm = [mo, mo, mc]
    case (2)
      rr = [r(2), r(3), r(1)]
      mm = [mo, mc, mo]
    case (3)
      rr = [r(3), r(2), r(1)]
      mm = [mo, mc, mo]
    end select
    call crdtrf(rr, mm, capr, theta, deriv)
    write(*,'(A,I1,2(1X,ES25.16E3),1X,L1)') 'CHART ', arrangement, &
      capr, theta, all(ieee_is_finite(deriv))
  end do
  call pes3d(r(1), r(2), r(3), v, grad)
  write(*,'(A,4(1X,ES25.16E3))') 'DIRECT', v, grad
  call co21appes(r, v, grad)
  write(*,'(A,4(1X,ES25.16E3))') 'WRAPPED', v, grad
  do axis = 1, 3
    do offset = -2, 2
      if (offset == 0) cycle
      xp = r
      xp(axis) = r(axis) + offset * 0.005d0
      call pes3d(xp(1), xp(2), xp(3), v, grad)
      ! A physical distance triple must satisfy all three triangle inequalities.
      write(*,'(A,I1,1X,I2,1X,L1,1X,ES25.16E3)') 'STENCIL ', axis, offset, &
        all(xp > 0d0) .and. 2d0*maxval(xp) <= sum(xp), v
    end do
  end do
end program trace_probe
