SUBROUTINE get_met_data(spinup,spinConv,met,soil,rad,                          &
    veg,kend,dels, TFRZ, ktau, kstart )
! Precision changes from REAL(4) to r_1 enable running with -r8


! Input arguments
LOGICAL, INTENT(IN)                    ::                                   &
     spinup,         & ! are we performing a spinup?
     spinConv          ! has model spinup converged?
TYPE(met_type),             INTENT(INOUT) :: met     ! meteorological data
TYPE (soil_parameter_type),INTENT(IN)  :: soil
TYPE (radiation_type),INTENT(IN)       :: rad
TYPE(veg_parameter_type),INTENT(INOUT) :: veg ! LAI retrieved from file
INTEGER, INTENT(IN)               :: ktau, &  ! timestep in loop including spinup
                                     kend, & ! total number of timesteps in run
                                     kstart  ! starting timestep
REAL,INTENT(IN)                   :: dels ! time step size
REAL, INTENT(IN) :: TFRZ

! Local variables
REAL(KIND=4),DIMENSION(1,1,1)          :: data3 ! temp variable for netcdf reading
REAL(KIND=4),DIMENSION(1,1,1,1)        :: data4 !  " " "
REAL(KIND=4),DIMENSION(1,1)            :: data2 ! " "
REAL(KIND=4),DIMENSION(1)              :: data1 ! " "
INTEGER                           :: i,j ! do loop counter
INTEGER                           :: ndims ! # of dimensions in file
REAL(KIND=4),ALLOCATABLE,DIMENSION(:)       :: tmpDat1
REAL(KIND=4),ALLOCATABLE,DIMENSION(:,:)     :: tmpDat2, tmpDat2x
REAL(KIND=4),ALLOCATABLE,DIMENSION(:,:,:)   :: tmpDat3, tmpDat3x
REAL(KIND=4),ALLOCATABLE,DIMENSION(:,:,:,:) :: tmpDat4, tmpDat4x

  DO i=1,mland ! over all land points/grid cells
    ! First set timing variables:
    ! All timing details below are initially written to the first patch
    ! of each gridcell, then dumped to all patches for the gridcell.
    IF(ktau==kstart) THEN ! initialise...
       SELECT CASE(time_coord)
       CASE('LOC')! i.e. use local time by default
          ! hour-of-day = starting hod
          met%hod(landpt(i)%cstart) = shod
          met%doy(landpt(i)%cstart) = sdoy
          met%moy(landpt(i)%cstart) = smoy
          met%year(landpt(i)%cstart) = syear
       CASE('GMT')! use GMT
          ! hour-of-day = starting hod + offset from GMT time:
          met%hod(landpt(i)%cstart) = shod + (longitude(i)/180.0)*12.0
          ! Note above that all met%* vars have dim mp,
          ! while longitude and latitude have dimension mland.
          met%doy(landpt(i)%cstart) = sdoy
          met%moy(landpt(i)%cstart) = smoy
          met%year(landpt(i)%cstart) = syear
       CASE DEFAULT
          CALL abort('Unknown time coordinate! ' &
               //' (SUBROUTINE get_met_data)')
       END SELECT
    ELSE
       ! increment hour-of-day by time step size:
       met%hod(landpt(i)%cstart) = met%hod(landpt(i)%cstart) + dels/3600.0
    END IF
    !
    IF(met%hod(landpt(i)%cstart)<0.0) THEN ! may be -ve since longitude
       ! has range [-180,180]
       ! Reduce day-of-year by one and ammend hour-of-day:
       met%doy(landpt(i)%cstart) = met%doy(landpt(i)%cstart) - 1
       met%hod(landpt(i)%cstart) = met%hod(landpt(i)%cstart) + 24.0
       ! If a leap year AND we're using leap year timing:
       if (is_leapyear(met%year(landpt(i)%cstart))) then
          SELECT CASE(INT(met%doy(landpt(i)%cstart)))
          CASE(0) ! ie Dec previous year
             met%moy(landpt(i)%cstart) = 12
             met%year(landpt(i)%cstart) = met%year(landpt(i)%cstart) - 1
             met%doy(landpt(i)%cstart) = 365 ! prev year not leap year as this is
          CASE(31) ! Jan
             met%moy(landpt(i)%cstart) = 1
          CASE(60) ! Feb
             met%moy(landpt(i)%cstart) = 2
          CASE(91) ! Mar
             met%moy(landpt(i)%cstart) = 3
          CASE(121)
             met%moy(landpt(i)%cstart) = 4
          CASE(152)
             met%moy(landpt(i)%cstart) = 5
          CASE(182)
             met%moy(landpt(i)%cstart) = 6
          CASE(213)
             met%moy(landpt(i)%cstart) = 7
          CASE(244)
             met%moy(landpt(i)%cstart) = 8
          CASE(274)
             met%moy(landpt(i)%cstart) = 9
          CASE(305)
             met%moy(landpt(i)%cstart) = 10
          CASE(335)
             met%moy(landpt(i)%cstart) = 11
          END SELECT
       ELSE ! not a leap year or not using leap year timing
          SELECT CASE(INT(met%doy(landpt(i)%cstart)))
          CASE(0) ! ie Dec previous year
             met%moy(landpt(i)%cstart) = 12
             met%year(landpt(i)%cstart) = met%year(landpt(i)%cstart) - 1
             ! If previous year is a leap year
             if (is_leapyear(met%year(landpt(i)%cstart))) then
                met%doy(landpt(i)%cstart) = 366
             ELSE
                met%doy(landpt(i)%cstart) = 365
             END IF
          CASE(31) ! Jan
             met%moy(landpt(i)%cstart) = 1
          CASE(59) ! Feb
             met%moy(landpt(i)%cstart) = 2
          CASE(90)
             met%moy(landpt(i)%cstart) = 3
          CASE(120)
             met%moy(landpt(i)%cstart) = 4
          CASE(151)
             met%moy(landpt(i)%cstart) = 5
          CASE(181)
             met%moy(landpt(i)%cstart) = 6
          CASE(212)
             met%moy(landpt(i)%cstart) = 7
          CASE(243)
             met%moy(landpt(i)%cstart) = 8
          CASE(273)
             met%moy(landpt(i)%cstart) = 9
          CASE(304)
             met%moy(landpt(i)%cstart) = 10
          CASE(334)
             met%moy(landpt(i)%cstart) = 11
          END SELECT
       END IF ! if leap year or not
    ELSE IF(met%hod(landpt(i)%cstart)>=24.0) THEN
       ! increment or GMT adj has shifted day
       ! Adjust day-of-year and hour-of-day:
       met%doy(landpt(i)%cstart) = met%doy(landpt(i)%cstart) + 1
       met%hod(landpt(i)%cstart) = met%hod(landpt(i)%cstart) - 24.0
       ! If a leap year AND we're using leap year timing:
        !! vh_js !! use is_leapyear function here instead of multiple conditions
       if (is_leapyear(met%year(landpt(i)%cstart))) then
          SELECT CASE(INT(met%doy(landpt(i)%cstart)))
          CASE(32) ! Feb
             met%moy(landpt(i)%cstart) = 2
          CASE(61) ! Mar
             met%moy(landpt(i)%cstart) = 3
          CASE(92)
             met%moy(landpt(i)%cstart) = 4
          CASE(122)
             met%moy(landpt(i)%cstart) = 5
          CASE(153)
             met%moy(landpt(i)%cstart) = 6
          CASE(183)
             met%moy(landpt(i)%cstart) = 7
          CASE(214)
             met%moy(landpt(i)%cstart) = 8
          CASE(245)
             met%moy(landpt(i)%cstart) = 9
          CASE(275)
             met%moy(landpt(i)%cstart) = 10
          CASE(306)
             met%moy(landpt(i)%cstart) = 11
          CASE(336)
             met%moy(landpt(i)%cstart) = 12
          CASE(367)! end of year; increment
             met%year(landpt(i)%cstart) = met%year(landpt(i)%cstart) + 1
             met%moy(landpt(i)%cstart) = 1
             met%doy(landpt(i)%cstart) = 1
          END SELECT
          ! ELSE IF not leap year and Dec 31st, increment year
       ELSE
          SELECT CASE(INT(met%doy(landpt(i)%cstart)))
          CASE(32) ! Feb
             met%moy(landpt(i)%cstart) = 2
          CASE(60) ! Mar
             met%moy(landpt(i)%cstart) = 3
          CASE(91)
             met%moy(landpt(i)%cstart) = 4
          CASE(121)
             met%moy(landpt(i)%cstart) = 5
          CASE(152)
             met%moy(landpt(i)%cstart) = 6
          CASE(182)
             met%moy(landpt(i)%cstart) = 7
          CASE(213)
             met%moy(landpt(i)%cstart) = 8
          CASE(244)
             met%moy(landpt(i)%cstart) = 9
          CASE(274)
             met%moy(landpt(i)%cstart) = 10
          CASE(305)
             met%moy(landpt(i)%cstart) = 11
          CASE(335)
             met%moy(landpt(i)%cstart) = 12
          CASE(366)! end of year; increment
             met%year(landpt(i)%cstart) = met%year(landpt(i)%cstart) + 1
             met%moy(landpt(i)%cstart) = 1
             met%doy(landpt(i)%cstart) = 1
          END SELECT
       END IF ! if leap year or not
    END IF ! if increment has pushed hod to a different day
    ! Now copy these values to all veg/soil patches in the current grid cell:
    met%hod(landpt(i)%cstart:landpt(i)%cend) = met%hod(landpt(i)%cstart)
    met%doy(landpt(i)%cstart:landpt(i)%cend) = met%doy(landpt(i)%cstart)
    met%moy(landpt(i)%cstart:landpt(i)%cend) = met%moy(landpt(i)%cstart)
    met%year(landpt(i)%cstart:landpt(i)%cend) = met%year(landpt(i)%cstart)
 ENDDO

 IF(metGrid=='mask') THEN
   ! N.B. not for GSWP runs, therefore only one met file here.
   ! Also, xdimsize and ydimsize are passed from io_variables.

   ALLOCATE(tmpDat2(xdimsize,ydimsize))
   ALLOCATE(tmpDat3(xdimsize,ydimsize,1))
   ALLOCATE(tmpDat4(xdimsize,ydimsize,1,1))
   ALLOCATE(tmpDat3x(xdimsize,ydimsize,nmetpatches))
   ALLOCATE(tmpDat4x(xdimsize,ydimsize,nmetpatches,1))

   ! Get SWdown data for mask grid:
   IF (cable_user%GSWP3) ncid_met=ncid_sw
   ok= NF90_GET_VAR(ncid_met,id%SWdown,tmpDat3, &
        start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading SWdown in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   ! Assign value to met data variable (no units change required):
   !jhan:quick fix, use (1/2) dimension 1 here arbitrarily
   DO i=1,mland ! over all land points/grid cells
     met%fsd(landpt(i)%cstart:landpt(i)%cend,1) = &
          0.5 * REAL(tmpDat3(land_x(i),land_y(i),1))
     met%fsd(landpt(i)%cstart:landpt(i)%cend,2) = &
          0.5 * REAL(tmpDat3(land_x(i),land_y(i),1))
   ENDDO

   ! Get Tair data for mask grid:- - - - - - - - - - - - - - - - - -
   IF(cable_user%GSWP3) ncid_met = ncid_ta
   ! Check if it's a 3D or 4D variable in file.
   ok = NF90_INQUIRE_VARIABLE(ncid_met,id%Tair,ndims=ndims)
      IF(ndims==3) THEN                                                 
         ok= NF90_GET_VAR(ncid_met,id%Tair,tmpDat3, &
               start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Tair in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
         met%tk(landpt(i)%cstart:landpt(i)%cend) = &
             REAL(tmpDat3(land_x(i),land_y(i),1)) + convert%Tair
         ENDDO
      ELSE
      ok= NF90_GET_VAR(ncid_met,id%Tair,tmpDat4, &
         start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
      IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Tair in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
      DO i=1,mland ! over all land points/grid cells
         met%tk(landpt(i)%cstart:landpt(i)%cend) = &
               REAL(tmpDat4(land_x(i),land_y(i),1,1)) + convert%Tair
      ENDDO
   END IF

   ! Get PSurf data for mask grid:- - - - - - - - - - - - - - - - - -
   if (cable_user%GSWP3) ncid_met = ncid_ps
   IF(exists%PSurf) THEN ! IF PSurf is in met file:
      ! Check if it's a 3D or 4D variable in file.
      ok = NF90_INQUIRE_VARIABLE(ncid_met,id%PSurf,ndims=ndims)
      IF(ndims==3) THEN                                                 
         ok= NF90_GET_VAR(ncid_met,id%PSurf,tmpDat3, &
               start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading PSurf in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
            met%pmb(landpt(i)%cstart:landpt(i)%cend) = &
               REAL(tmpDat3(land_x(i),land_y(i),1)) * convert%PSurf
         ENDDO
      ELSE
         ok= NF90_GET_VAR(ncid_met,id%PSurf,tmpDat4, &
            start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
               (ok,'Error reading PSurf in met data file ' &
               //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
            met%pmb(landpt(i)%cstart:landpt(i)%cend) = &
                  REAL(tmpDat4(land_x(i),land_y(i),1,1)) * convert%PSurf
         ENDDO
      END IF
   ELSE ! PSurf must be fixed as a function of site elevation and T:
      DO i=1,mland ! over all land points/grid cells
         met%pmb(landpt(i)%cstart:landpt(i)%cend)=1013.25* &
            (met%tk(landpt(i)%cstart)/(met%tk(landpt(i)%cstart) + 0.0065* &
            elevation(i)))**(9.80665/287.04/0.0065)
      ENDDO
   END IF

   ! Get Qair data for mask grid: - - - - - - - - - - - - - - - - - -
   IF(cable_user%GSWP3) ncid_met = ncid_qa
   ! Check if it's a 3D or 4D variable in file.
   ok = NF90_INQUIRE_VARIABLE(ncid_met,id%Qair,ndims=ndims)
      IF(ndims==3) THEN                                                 
         ok= NF90_GET_VAR(ncid_met,id%Qair,tmpDat3, &
               start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Qair in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
      IF(convert%Qair==-999.0) THEN
      ! Convert relative value using only first veg/soil patch values
      ! (identical)
         DO i=1,mland ! over all land points/grid cells
            CALL rh_sh(REAL(tmpDat3(land_x(i),land_y(i),1)), &
                  met%tk(landpt(i)%cstart), &
                  met%pmb(landpt(i)%cstart),met%qv(landpt(i)%cstart))
            met%qv(landpt(i)%cstart:landpt(i)%cend) = met%qv(landpt(i)%cstart)
         ENDDO
      ELSE
         DO i=1,mland ! over all land points/grid cells
            met%qv(landpt(i)%cstart:landpt(i)%cend) = &
                  REAL(tmpDat3(land_x(i),land_y(i),1))
         ENDDO
      END IF
      ELSE
      ok= NF90_GET_VAR(ncid_met,id%Qair,tmpDat4, &
         start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
      IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Qair in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
      IF(convert%Qair==-999.0) THEN
         ! Convert relative value using only first veg/soil patch values
         ! (identical)
         DO i=1,mland ! over all land points/grid cells
            CALL rh_sh(REAL(tmpDat4(land_x(i),land_y(i),1,1)), &
                  met%tk(landpt(i)%cstart), &
                  met%pmb(landpt(i)%cstart),met%qv(landpt(i)%cstart))
            met%qv(landpt(i)%cstart:landpt(i)%cend) = met%qv(landpt(i)%cstart)
         ENDDO
      ELSE
         DO i=1,mland ! over all land points/grid cells
            met%qv(landpt(i)%cstart:landpt(i)%cend) = &
                  REAL(tmpDat4(land_x(i),land_y(i),1,1))
         ENDDO 
      END IF
   END IF
      
   ! Get Wind data for mask grid: - - - - - - - - - - - - - - - - - -
 IF(cable_user%GSWP3) ncid_met = ncid_wd
   ! Check if it's a 3D or 4D variable in file.
   ok = NF90_INQUIRE_VARIABLE(ncid_met,id%Wind,ndims=ndims)
   IF(ndims==3) THEN                                                 
      IF(exists%Wind) THEN ! Scalar Wind
         ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat3, &
               start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Wind in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
            met%ua(landpt(i)%cstart:landpt(i)%cend) = &
               REAL(tmpDat3(land_x(i),land_y(i),1))
         ENDDO
      ELSE ! Vector wind
         ! Get Wind_N:
         ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat3, &
            start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Wind_N in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         ! only part of wind variable
         DO i=1,mland ! over all land points/grid cells
         met%ua(landpt(i)%cstart) = REAL(tmpDat3(land_x(i),land_y(i),1))
         ENDDO
         ok= NF90_GET_VAR(ncid_met,id%Wind_E,tmpDat3, &
            start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Wind_E in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         ! Write final scalar Wind value:
         DO i=1,mland ! over all land points/grid cells
         met%ua(landpt(i)%cstart:landpt(i)%cend) = &
               SQRT(met%ua(landpt(i)%cstart)**2 + &
               REAL(tmpDat3(land_x(i),land_y(i),1))**2)
         ENDDO
      END IF
   ELSE
      IF(exists%Wind) THEN ! Scalar Wind
         ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat4, &
            start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
               (ok,'Error reading Wind in met data file ' &
               //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
            met%ua(landpt(i)%cstart:landpt(i)%cend) = &
                  REAL(tmpDat4(land_x(i),land_y(i),1,1))
         ENDDO
      ELSE ! Vector wind
         ! Get Wind_N:
         ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat4, &
            start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Wind_N in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         ! only part of wind variable
         DO i=1,mland ! over all land points/grid cells
         met%ua(landpt(i)%cstart) = REAL(tmpDat4(land_x(i),land_y(i),1,1))
         ENDDO
         ok= NF90_GET_VAR(ncid_met,id%Wind_E,tmpDat4, &
            start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
            (ok,'Error reading Wind_E in met data file ' &
            //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         ! Write final scalar Wind value:
         DO i=1,mland ! over all land points/grid cells
         met%ua(landpt(i)%cstart:landpt(i)%cend) = &
               SQRT(met%ua(landpt(i)%cstart)**2 + &
               REAL(tmpDat4(land_x(i),land_y(i),1,1))**2)
         ENDDO
      END IF
   END IF

   ! Get Rainf and Snowf data for mask grid:- - - - - - - - - - - - -
   if (cable_user%GSWP3) ncid_met = ncid_rain
   ok= NF90_GET_VAR(ncid_met,id%Rainf,tmpDat3, &
        start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading Rainf in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   DO i=1,mland ! over all land points/grid cells
     met%precip(landpt(i)%cstart:landpt(i)%cend) = &
          REAL(tmpDat3(land_x(i),land_y(i),1)) ! store Rainf
   ENDDO
   IF(exists%Snowf) THEN
     if (cable_user%GSWP3) ncid_met = ncid_snow
     ok= NF90_GET_VAR(ncid_met,id%Snowf,tmpDat3, &
          start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading Snowf in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     ! store Snowf value (EK nov2007)
     DO i=1,mland ! over all land points/grid cells
       met%precip_sn(landpt(i)%cstart:landpt(i)%cend) = &
            REAL(tmpDat3(land_x(i),land_y(i),1))
     ENDDO
   ELSE
     met%precip_sn(:) = 0.0
   END IF
   ! combine Rainf and Snowf data
   met%precip(:) = met%precip(:) + met%precip_sn(:)
   ! Convert units:
   met%precip(:) = met%precip(:) * convert%Rainf
   met%precip_sn(:) = met%precip_sn(:) * convert%Rainf
   ! If we're performing a spinup, the spinup hasn't converged,
   ! and an avPrecip variable has been found, modify precip to
   ! ensure reasonable equilibration:
   IF(spinup.AND.(.NOT.spinConv).AND.exists%avPrecip) THEN
     ! Rescale precip to average rainfall for this site:
     DO i=1,mland ! over all land points/grid cells
       met%precip(landpt(i)%cstart:landpt(i)%cend) = &
            met%precip(landpt(i)%cstart) / PrecipScale(i)
       ! Added for snow (EK nov2007)
       met%precip_sn(landpt(i)%cstart:landpt(i)%cend) = &
            met%precip_sn(landpt(i)%cstart) / PrecipScale(i)
     ENDDO
   END IF

   ! Get LWdown data for mask grid: - - - - - - - - - - - - - - - - -
   if (cable_user%GSWP3) ncid_met = ncid_lw
   IF(exists%LWdown) THEN ! If LWdown exists in met file
     ok= NF90_GET_VAR(ncid_met,id%LWdown,tmpDat3, &
          start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading LWdown in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     DO i=1,mland ! over all land points/grid cells
       met%fld(landpt(i)%cstart:landpt(i)%cend) = &
            REAL(tmpDat3(land_x(i),land_y(i),1))
     ENDDO
   ELSE ! Synthesise LWdown based on temperature
     ! Use Swinbank formula:
     met%fld(:) = 0.0000094*0.0000000567*(met%tk(:)**6.0)
   END IF

   ! Get CO2air data for mask grid:- - - - - - - - - - - - - - - - - -
   IF(exists%CO2air) THEN ! If CO2air exists in met file
      ! Check if it's a 3D or 4D variable in file.
      ok = NF90_INQUIRE_VARIABLE(ncid_met,id%CO2air,ndims=ndims)
         IF(ndims==3) THEN                                                 
            ok= NF90_GET_VAR(ncid_met,id%CO2air,tmpDat3, &
                  start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
            IF(ok /= NF90_NOERR) CALL nc_abort &
                  (ok,'Error reading CO2air in met data file ' &
                  //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
            DO i=1,mland ! over all land points/grid cells
               met%ca(landpt(i)%cstart:landpt(i)%cend) = &
                     REAL(tmpDat3(land_x(i),land_y(i),1))/1000000.0
            ENDDO
         ELSE
            ok= NF90_GET_VAR(ncid_met,id%CO2air,tmpDat4, &
                  start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,1,1/))
            IF(ok /= NF90_NOERR) CALL nc_abort &
                  (ok,'Error reading CO2air in met data file ' &
                  //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
            DO i=1,mland ! over all land points/grid cells
               met%ca(landpt(i)%cstart:landpt(i)%cend) = &
                     REAL(tmpDat4(land_x(i),land_y(i),1,1))/1000000.0
            ENDDO
         END IF
   ELSE
     ! Fix CO2 air concentration:
     met%ca(:) = fixedCO2 /1000000.0
   END IF

   ! Get LAI, if it's present, for mask grid:- - - - - - - - - - - - -
   IF(exists%LAI) THEN ! If LAI exists in met file
     IF(exists%LAI_T) THEN ! i.e. time dependent LAI
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat4x, &
              start=(/1,1,1,ktau/),count=(/xdimsize,ydimsize,nmetpatches,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met1 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           DO j=1,nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = &
                  REAL(tmpDat4x(land_x(i),land_y(i),j,1))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat3, &
              start=(/1,1,ktau/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met2 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = &
                REAL(tmpDat3(land_x(i),land_y(i),1))
         ENDDO
       END IF
     ELSEIF(exists%LAI_M) THEN ! i.e. monthly LAI (BP apr08)
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat4x, &
              start=(/1,1,1,met%moy/),count=(/xdimsize,ydimsize,nmetpatches,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met3 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           DO j=1,nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = &
                  REAL(tmpDat4x(land_x(i),land_y(i),j,1))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat3, &
              start=(/1,1,met%moy/),count=(/xdimsize,ydimsize,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met4 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = &
                REAL(tmpDat3(land_x(i),land_y(i),1))
         ENDDO
       END IF
     ELSE ! i.e. time independent LAI
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat3x, &
              start=(/1,1,1/),count=(/xdimsize,ydimsize,nmetpatches/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met5 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           DO j=1,nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = &
                  REAL(tmpDat3x(land_x(i),land_y(i),j))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat2, &
              start=(/1,1/),count=(/xdimsize,ydimsize/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met6 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = &
                REAL(tmpDat2(land_x(i),land_y(i)))
         ENDDO
       END IF
     END IF
   ELSE
     ! If not in met file, use default LAI value:
     DO i=1,mland ! over all land points/grid cells

        veg%vlai(landpt(i)%cstart:landpt(i)%cend) =  &
             defaultLAI(landpt(i)%cstart:landpt(i)%cend,met%moy(landpt(i)%cstart))
          
     ENDDO
   END IF


   DEALLOCATE(tmpDat2,tmpDat3,tmpDat4,tmpDat3x,tmpDat4x)

 ELSE IF(metGrid=='land') THEN

   ! Collect data from land only grid in netcdf file:
   ALLOCATE(tmpDat1(mland))
   ALLOCATE(tmpDat2(mland,1))
   ALLOCATE(tmpDat2x(mland,nmetpatches))
   ALLOCATE(tmpDat3(mland,nmetpatches,1))

   ! Get SWdown data for land-only grid: - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_sw
   ok= NF90_GET_VAR(ncid_met,id%SWdown,tmpDat2, &
        start=(/1,ktau/),count=(/mland,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading SWdown in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   ! Assign value to met data variable (no units change required):
   DO i=1,mland ! over all land points/grid cells
     met%fsd(landpt(i)%cstart:landpt(i)%cend,1) = 0.5*REAL(tmpDat2(i,1))
     met%fsd(landpt(i)%cstart:landpt(i)%cend,2) = 0.5*REAL(tmpDat2(i,1))
   ENDDO

   ! Get Tair data for land-only grid:- - - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_ta
   ok= NF90_GET_VAR(ncid_met,id%Tair,tmpDat2, &
        start=(/1,ktau/),count=(/mland,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading Tair in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   ! Assign value to met data variable with units change:
   DO i=1,mland ! over all land points/grid cells
     met%tk(landpt(i)%cstart:landpt(i)%cend) = &
          REAL(tmpDat2(i,1)) + convert%Tair
   ENDDO

   ! Get PSurf data for land-only grid:- -- - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_ps
   IF(exists%PSurf) THEN ! IF PSurf is in met file:
     IF ((ncciy == 1986) .AND. (ktau == 2184)) THEN
       !hzz to fix the problem of ps data on time step 2184
       ok= NF90_GET_VAR(ncid_met,id%PSurf,tmpDat2, &
            start=(/1,2176/),count=(/mland,1/)) ! fixing bug in GSWP ps data
     ELSE
       ok= NF90_GET_VAR(ncid_met,id%PSurf,tmpDat2, &
            start=(/1,ktau/),count=(/mland,1/))
     ENDIF
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading PSurf in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     DO i=1,mland ! over all land points/grid cells
       met%pmb(landpt(i)%cstart:landpt(i)%cend) = &
            REAL(tmpDat2(i,1)) * convert%PSurf
     ENDDO
   ELSE ! PSurf must be fixed as a function of site elevation and T:
     DO i=1,mland ! over all land points/grid cells
       met%pmb(landpt(i)%cstart:landpt(i)%cend) = 1013.25 &
            *(met%tk(landpt(i)%cstart)/(met%tk(landpt(i)%cstart) &
            + 0.0065*elevation(i)))**(9.80665/287.04/0.0065)
     ENDDO
   END IF

   ! Get Qair data for land-only grid:- - - - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_qa
   ok= NF90_GET_VAR(ncid_met,id%Qair,tmpDat2, &
        start=(/1,ktau/),count=(/mland,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading Qair in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   IF(convert%Qair==-999.0) THEN
     DO i=1,mland ! over all land points/grid cells
       CALL rh_sh(REAL(tmpDat2(i,1)), met%tk(landpt(i)%cstart), &
            met%pmb(landpt(i)%cstart),met%qv(landpt(i)%cstart))
       met%qv(landpt(i)%cstart:landpt(i)%cend)=met%qv(landpt(i)%cstart)
     ENDDO
   ELSE
     DO i=1,mland ! over all land points/grid cells
       met%qv(landpt(i)%cstart:landpt(i)%cend) = REAL(tmpDat2(i,1))
     ENDDO
   END IF

   ! Get Wind data for land-only grid: - - - - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_wd
   IF(exists%Wind) THEN ! Scalar Wind
     ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading Wind in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     ! Assign value to met data variable (no units change required):
     DO i=1,mland ! over all land points/grid cells
       met%ua(landpt(i)%cstart:landpt(i)%cend) = REAL(tmpDat2(i,1))
     ENDDO
   ELSE ! Vector wind
     ! Get Wind_N:
     ok= NF90_GET_VAR(ncid_met,id%Wind,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading Wind_N in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     ! write part of the wind variable
     met%ua(landpt(:)%cstart) = REAL(tmpDat2(:,1))
     ok= NF90_GET_VAR(ncid_met,id%Wind_E,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading Wind_E in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     ! Write final scalar Wind value:
     DO i=1,mland ! over all land points/grid cells
       met%ua(landpt(i)%cstart:landpt(i)%cend) = &
            SQRT(met%ua(landpt(i)%cstart)**2 + REAL(tmpDat2(i,1))**2)
     ENDDO
   END IF

   ! Get Rainf and Snowf data for land-only grid: - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_rain
   ok= NF90_GET_VAR(ncid_met,id%Rainf,tmpDat2, &
        start=(/1,ktau/),count=(/mland,1/))
   IF(ok /= NF90_NOERR) CALL nc_abort &
        (ok,'Error reading Rainf in met data file ' &
        //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
   DO i=1,mland ! over all land points/grid cells
     met%precip(landpt(i)%cstart:landpt(i)%cend) = REAL(tmpDat2(i,1))
   ENDDO

   IF (ncciy > 0) ncid_met = ncid_snow
   IF(exists%Snowf) THEN
     ok= NF90_GET_VAR(ncid_met,id%Snowf,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading Snowf in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     DO i=1,mland ! over all land points/grid cells
       met%precip_sn(landpt(i)%cstart:landpt(i)%cend) = &
            REAL(tmpDat2(i,1))
     ENDDO
   ELSE
     met%precip_sn(:) = 0.0
   END IF

   ! combine Rainf and Snowf data
   met%precip(:) = met%precip(:) + met%precip_sn(:)
   ! Convert units:
   met%precip(:) = met%precip(:) * convert%Rainf
   met%precip_sn(:) = met%precip_sn(:) * convert%Rainf
   ! If we're performing a spinup, the spinup hasn't converged,
   ! and an avPrecip variable has been found, modify precip to
   ! ensure reasonable equilibration:
   IF(spinup.AND.(.NOT.spinConv).AND.exists%avPrecip) THEN
     ! Rescale precip to average rainfall for this site:
     DO i=1,mland ! over all land points/grid cells
       met%precip(landpt(i)%cstart:landpt(i)%cend) = &
            met%precip(landpt(i)%cstart) / PrecipScale(i)
       met%precip_sn(landpt(i)%cstart:landpt(i)%cend) = &
            met%precip_sn(landpt(i)%cstart) / PrecipScale(i)
     ENDDO
   END IF

   ! Get LWdown data for land-only grid: - - - - - - - - - - - - - -
   IF (ncciy > 0) ncid_met = ncid_lw
   IF(exists%LWdown) THEN ! If LWdown exists in met file
     ok= NF90_GET_VAR(ncid_met,id%LWdown,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading LWdown in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     DO i=1,mland ! over all land points/grid cells
       met%fld(landpt(i)%cstart:landpt(i)%cend) = REAL(tmpDat2(i,1))
     ENDDO
   ELSE ! Synthesise LWdown based on temperature
     ! Use Swinbank formula:
     met%fld(:) = 0.0000094*0.0000000567*(met%tk(:)**6.0)
   END IF

   ! Get CO2air data for land-only grid:- - - - - - - - - - - - - -
   IF(exists%CO2air) THEN ! If CO2air exists in met file
     ok= NF90_GET_VAR(ncid_met,id%CO2air,tmpDat2, &
          start=(/1,ktau/),count=(/mland,1/))
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading CO2air in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
     DO i=1,mland ! over all land points/grid cells
       met%ca(landpt(i)%cstart:landpt(i)%cend) = &
            REAL(tmpDat2(i,1)) / 1000000.0
     ENDDO
   ELSE
     met%ca(:) = fixedCO2 /1000000.0
   END IF

   ! Get LAI data, if it exists, for land-only grid:- - - - - - - - -
   IF(exists%LAI) THEN ! If LAI exists in met file
     IF(exists%LAI_T) THEN ! i.e. time dependent LAI
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat3, &
              start=(/1,1,ktau/),count=(/mland,nmetpatches,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met7 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           IF ( (landpt(i)%cend - landpt(i)%cstart + 1) < nmetpatches) THEN
             PRINT *, 'not enough patches at land point ', i
             STOP
           END IF
           DO j=1, nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = REAL(tmpDat3(i,j,1))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat2, &
              start=(/1,ktau/),count=(/mland,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met8 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = &
                REAL(tmpDat2(i,1))
         ENDDO
       END IF
     ELSEIF(exists%LAI_M) THEN ! i.e. monthly LAI (BP apr08)
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat3, &
              start=(/1,1,met%moy/),count=(/mland,nmetpatches,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met9 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           DO j=1, nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = REAL(tmpDat3(i,j,1))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat2, &
              start=(/1,met%moy/),count=(/mland,1/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met10 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = &
                REAL(tmpDat2(i,1))
         ENDDO
       END IF
     ELSE ! LAI time independent
       IF(exists%LAI_P) THEN ! i.e. patch dependent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat2x, &
              start=(/1,1/),count=(/mland,nmetpatches/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met11 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           DO j=1, nmetpatches
             veg%vlai(landpt(i)%cstart+j-1) = REAL(tmpDat2x(i,j))
           ENDDO
         ENDDO
       ELSE ! i.e. patch independent LAI
         ok= NF90_GET_VAR(ncid_met,id%LAI,tmpDat1, &
              start=(/1/),count=(/mland/))
         IF(ok /= NF90_NOERR) CALL nc_abort &
              (ok,'Error reading LAI in met12 data file ' &
              //TRIM(filename%met)//' (SUBROUTINE get_met_data)')
         DO i=1,mland ! over all land points/grid cells
           veg%vlai(landpt(i)%cstart:landpt(i)%cend) = REAL(tmpDat1(i))
         ENDDO
       END IF
     END IF
   ELSE
     ! If not in met file, use default LAI value:
     DO i=1,mland ! over all land points/grid cells
      !! vh_js !! corrected indices of defaultLAI
       veg%vlai(landpt(i)%cstart:landpt(i)%cend) =  &
            defaultLAI(landpt(i)%cstart:landpt(i)%cend,met%moy(landpt(i)%cstart))



     ENDDO

   END IF
   DEALLOCATE(tmpDat1, tmpDat2, tmpDat3, tmpDat2x)

 ELSE
   CALL abort('Unrecognised grid type')
 END IF ! grid type

 if ((.not. exists%Snowf) .or. all(met%precip_sn == 0.0)) then ! honour snowf input
 DO i=1,mland ! over all land points/grid cells
   ! Set solid precip based on temp
   met%precip_sn(landpt(i)%cstart:landpt(i)%cend) = 0.0 ! (EK nov2007)
   IF( met%tk(landpt(i)%cstart) <= tfrz ) &
        met%precip_sn(landpt(i)%cstart:landpt(i)%cend) &
        = met%precip(landpt(i)%cstart) ! (EK nov2007)
 END DO ! 1, mland over all land grid points
 endif

 ! Set cosine of zenith angle (provided by GCM when online):
 met%coszen = sinbet(met%doy, rad%latitude, met%hod)
 ! initialise within canopy air temp
 met%tvair = met%tk
 met%tvrad = met%tk
 IF(check%ranges) THEN
    ! Check ranges are okay:
       !jhan:quick fix, use dimension 1 here arbitrarily
    IF(ANY(met%fsd(:,1)<ranges%SWdown(1)).OR.ANY(met%fsd(:,1)>ranges%SWdown(2))) &
         CALL abort('SWdown out of specified ranges!')
    IF(ANY(met%fsd(:,2)<ranges%SWdown(1)).OR.ANY(met%fsd(:,2)>ranges%SWdown(2))) &
         CALL abort('SWdown out of specified ranges!')
    IF(ANY(met%fld<ranges%LWdown(1)).OR.ANY(met%fld>ranges%LWdown(2))) &
         CALL abort('LWdown out of specified ranges!')
    IF(ANY(met%qv<ranges%Qair(1)).OR.ANY(met%qv>ranges%Qair(2))) &
         CALL abort('Qair out of specified ranges!')
    IF(ANY(met%precip<ranges%Rainf(1)).OR.ANY(met%precip>ranges%Rainf(2))) then
       CALL abort('Rainf out of specified ranges!')
    ENDIF
    IF(ANY(met%ua<ranges%Wind(1)).OR.ANY(met%ua>ranges%Wind(2))) &
         CALL abort('Wind out of specified ranges!')
    IF(ANY(met%tk<ranges%Tair(1)).OR.ANY(met%tk>ranges%Tair(2))) &
         CALL abort('Tair out of specified ranges!')
    IF(ANY(met%pmb<ranges%PSurf(1)).OR.ANY(met%pmb>ranges%PSurf(2))) then
       write(*,*) "min, max Psurf", minval(met%pmb), maxval(met%pmb),ranges%Psurf(1), ranges%Psurf(2)
         CALL abort('PSurf out of specified ranges!')
    endif
 END IF

END SUBROUTINE get_met_data