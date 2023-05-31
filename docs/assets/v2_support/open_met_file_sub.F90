SUBROUTINE open_met_file(dels,koffset,kend,spinup, TFRZ)

    USE CABLE_COMMON_MODULE, ONLY : IS_LEAPYEAR, YMDHMS2DOYSOD, DOYSOD2YMDHMS,&
                                    HANDLE_ERR
    IMPLICIT NONE
    ! Input arguments
    REAL, INTENT(OUT) :: dels   ! time step size
    REAL, INTENT(IN) :: TFRZ
    INTEGER, INTENT(INOUT)      :: koffset ! offset between met file and desired period
    INTEGER, INTENT(OUT)        :: kend   ! number of time steps in simulation
    LOGICAL, INTENT(IN)              :: spinup ! will a model spinup be performed?
 
    ! Local variables
    INTEGER                     ::                                         &
         timevarID,              & ! time variable ID number
         xdimID,                 & ! x dimension ID numbers
         ydimID,                 & ! y dimension ID numbers
         patchdimID,             & ! patch dimension ID
         monthlydimID,           & ! month dimension ID for LAI info
         maskID,                 & ! mask variable ID
         landID,                 & ! land variable ID
         landdimID,              & ! land dimension ID
         latitudeID,             & ! lat variable IDs
         longitudeID,            & ! lon variable IDs
         edoy,                   & ! end time day-of-year
         eyear,                  & ! end time year
         jump_days,              & ! days made by first "time" entry
         sdoytmp,                & ! used to determine start time hour-of-day
         mland_ctr,              & ! counter for number of land points read from file
         mland_fromfile,         & ! number of land points in file
         lai_dims,               & ! number of dims of LAI var if in met file
         iveg_dims,              & ! number of dims of iveg var if in met file
         isoil_dims,             & ! number of dims of isoil var if in met file
         tsmin,tsdoy,tsyear,     & ! temporary variables
         x,y,i,j,                & ! do loop counters
         tempmonth,                              &
         ssod, &
         nsod, &
         LOY, &
         iday,&
         imin,&
         isec,&
         ishod, &
         dnsec  = 0
    INTEGER,DIMENSION(1)        ::                                         &
         timedimID,              & ! time dimension ID number
         data1i                    ! temp variable for netcdf reading
    INTEGER,DIMENSION(4)        :: laidimids ! for checking lai variable
    INTEGER,DIMENSION(1,1)      :: data2i ! temp variable for netcdf reading
    INTEGER,POINTER,DIMENSION(:)     ::land_xtmp,land_ytmp ! temp indicies
    REAL,POINTER, DIMENSION(:)  :: lat_temp, lon_temp ! lat and lon
    REAL                        ::                                         &
         tshod,                  & ! temporary variable
         ehod,                   & ! end time hour-of-day
         precipTot,              & ! used for spinup adj
         avPrecipInMet             ! used for spinup adj
    CHARACTER(LEN=10)                :: todaydate, nowtime ! used to timestamp log file
    REAL(4),DIMENSION(1)             :: data1 ! temp variable for netcdf reading
    REAL(4),DIMENSION(1,1)           :: data2 ! temp variable for netcdf reading
    REAL(4), DIMENSION(:),     ALLOCATABLE :: temparray1  ! temp read in variable
    REAL(4), DIMENSION(:,:),   ALLOCATABLE :: &
         tempPrecip2,            & ! used for spinup adj
         temparray2                ! temp read in variable
    REAL(4), DIMENSION(:,:,:), ALLOCATABLE :: tempPrecip3 ! used for spinup adj
    LOGICAL                          ::                                         &
         all_met,LAT1D,LON1D     ! ALL required met in met file (no synthesis)?
 
     ! Initialise parameter loading switch - will be set to TRUE when
     ! parameters are loaded:
     exists%parameters = .FALSE. ! initialise
     ! Initialise initialisation loading switch - will be set to TRUE when
     ! initialisation data are loaded:
     exists%initial = .FALSE. ! initialise
 
     LAT1D = .false.
     LON1D = .false.
 
     ! Write filename to log file:
     WRITE(logn,*) '============================================================'
     WRITE(logn,*) 'Log file for offline CABLE run:'
     CALL DATE_AND_TIME(todaydate, nowtime)
     todaydate=todaydate(1:4)//'/'//todaydate(5:6)//'/'//todaydate(7:8)
     nowtime=nowtime(1:2)//':'//nowtime(3:4)//':'//nowtime(5:6)
     WRITE(logn,*) TRIM(nowtime),' ',TRIM(todaydate)
     WRITE(logn,*) '============================================================'
 
     ! Open netcdf file:
   IF (ncciy > 0) THEN
     WRITE(logn,*) 'Opening met data file: ', TRIM(gswpfile%rainf), ' and 7 more'
     ok = NF90_OPEN(gswpfile%rainf,0,ncid_rain)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'rainf'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%snowf,0,ncid_snow)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'snow'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%LWdown,0,ncid_lw)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'lw'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%SWdown,0,ncid_sw)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'sw'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%PSurf,0,ncid_ps)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'ps'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%Qair,0,ncid_qa)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'qa'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%Tair,0,ncid_ta)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'ta'
           CALL handle_err( ok )
        ENDIF
     ok = NF90_OPEN(gswpfile%wind,0,ncid_wd)
        IF (ok /= NF90_NOERR) THEN
           PRINT*,'wind',ncid_wd
           CALL handle_err( ok )
        ENDIF
        if (cable_user%GSWP3) then
           ok = NF90_OPEN(gswpfile%mask,0,ncid_mask)
           if (ok .ne. NF90_NOERR) then
              CALL nc_abort(ok, "Error opening GSWP3 mask file")
           end if
           LAT1D = .true.   !GSWP3 forcing has 1d lat/lon variables
           LON1D = .true.  
        else
           ncid_mask = ncid_rain
        end if
        ncid_met = ncid_rain
   ELSE
     WRITE(logn,*) 'Opening met data file: ', TRIM(filename%met)
     ok = NF90_OPEN(filename%met,0,ncid_met) ! open met data file
     IF (ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error opening netcdf met forcing file '//TRIM(filename%met)// &
          ' (SUBROUTINE open_met_file)')
   ENDIF
 
     !!=====================VV Determine spatial details VV=================
     ! Determine number of sites/gridcells.
     ! Find size of 'x' or 'lon' dimension:
     ok = NF90_INQ_DIMID(ncid_met,'x', xdimID)
     IF(ok/=NF90_NOERR) THEN ! if failed
        ! Try 'lon' instead of x
        ok = NF90_INQ_DIMID(ncid_met,'lon', xdimID)
        IF(ok/=NF90_NOERR) CALL nc_abort &
             (ok,'Error finding x dimension in '&
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     END IF
     ok = NF90_INQUIRE_DIMENSION(ncid_met,xdimID,len=xdimsize)
     IF(ok/=NF90_NOERR) CALL nc_abort &
          (ok,'Error determining size of x dimension in ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Find size of 'y' dimension:
     ok = NF90_INQ_DIMID(ncid_met,'y', ydimID)
     IF(ok/=NF90_NOERR) THEN ! if failed
        ! Try 'lat' instead of y
        ok = NF90_INQ_DIMID(ncid_met,'lat', ydimID)
        IF(ok/=NF90_NOERR) CALL nc_abort &
             (ok,'Error finding y dimension in ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     END IF
     ok = NF90_INQUIRE_DIMENSION(ncid_met,ydimID,len=ydimsize)
     IF(ok/=NF90_NOERR) CALL nc_abort &
          (ok,'Error determining size of y dimension in ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Determine number of gridcells in netcdf file:
     ngridcells = xdimsize*ydimsize
     WRITE(logn,'(A28,I7)') 'Total number of gridcells: ', ngridcells
 
     ! Get all latitude and longitude values.
     ! Find latitude variable (try 'latitude' and 'nav_lat'(ALMA)):
     ok = NF90_INQ_VARID(ncid_met, 'latitude', latitudeID)
     IF(ok /= NF90_NOERR) THEN
        ok = NF90_INQ_VARID(ncid_met, 'nav_lat', latitudeID)
        IF(ok /= NF90_NOERR) THEN
           !MDeck allow for 1d lat called 'lat'
           ok = NF90_INQ_VARID(ncid_met, 'lat', latitudeID)
           if (ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding latitude variable in ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        END IF
     END IF
     ! Allocate space for lat_all variable and its temp counterpart:
     ALLOCATE(lat_all(xdimsize,ydimsize))
     ALLOCATE(temparray2(xdimsize,ydimsize))
    !MDeck allow for 1d lat called 'lat'
     ! Get latitude values for entire region:
     IF (.not.LAT1D) THEN
        ok= NF90_GET_VAR(ncid_met,latitudeID,temparray2)
     ELSE
        DO x=1,xdimsize
           ok= NF90_GET_VAR(ncid_met,latitudeID,temparray2(x,:))
        ENDDO
     END IF
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading latitude variable in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Needed since r_1 will be double precision with -r8:
     lat_all = REAL(temparray2)
     ! Find longitude variable (try 'longitude' and 'nav_lon'(ALMA)):
     ok = NF90_INQ_VARID(ncid_met, 'longitude', longitudeID)
     IF(ok /= NF90_NOERR) THEN
        ok = NF90_INQ_VARID(ncid_met, 'nav_lon', longitudeID)
        IF(ok /= NF90_NOERR) THEN
           !MDeck allow for 1d lon called 'lon'
           ok = NF90_INQ_VARID(ncid_met, 'lon', longitudeID)
           IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding longitude variable in ' &
              //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        END IF
     END IF
     ! Allocate space for lon_all variable:
     ALLOCATE(lon_all(xdimsize,ydimsize))
     ! Get longitude values for entire region:
     !MDeck allow for 1d lon
     IF (.not.LON1D) then
        ok= NF90_GET_VAR(ncid_met,longitudeID,temparray2)
     ELSE
        DO y=1,ydimsize
           ok= NF90_GET_VAR(ncid_met,longitudeID,temparray2(:,y))
        ENDDO
     END IF
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading longitude variable in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Needed since r_1 will be double precision with -r8:
     lon_all = REAL(temparray2)
     DEALLOCATE(temparray2)
 
     ! Check for "mask" variable or "land" variable to tell grid type
     ! (and allow neither if only one gridpoint). "mask" is a 2D variable
     ! with dims x,y and "land" is a 1D variable.
     if (.not.cable_user%gswp3) then
        ok = NF90_INQ_VARID(ncid_mask, 'mask', maskID) ! check for "mask" 
     else
        ok = NF90_INQ_VARID(ncid_mask, 'landsea', maskID) ! check for "mask" 
     end if
     IF(ok /= NF90_NOERR) THEN ! if error, i.e. no "mask" variable:
        ! Check for "land" variable:
        ok = NF90_INQ_VARID(ncid_met, 'land', landID)
        IF(ok /= NF90_NOERR) THEN ! ie no "land" or "mask"
           IF(ngridcells==1) THEN
              ! Allow no explicit grid system if only one gridpoint
              ALLOCATE(mask(xdimsize,ydimsize)) ! Allocate "mask" variable
              metGrid='mask' ! Use mask system, one gridpoint.
              mask = 1
              ALLOCATE(latitude(1),longitude(1))
              latitude = lat_all(1,1)
              longitude = lon_all(1,1)
              mland_fromfile=1
              ALLOCATE(land_x(mland_fromfile),land_y(mland_fromfile))
              land_x = 1
              land_y = 1
           ELSE
              ! Call abort if more than one gridcell and no
              ! recognised grid system:
              CALL nc_abort &
                   (ok,'Error finding grid system ("mask" or "land") variable in ' &
                   //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           END IF
        ELSE ! i.e. "land" variable exists
           metGrid='land'
           ! Check size of "land" dimension:
           ok = NF90_INQ_DIMID(ncid_met,'land', landdimID)
           IF(ok/=NF90_NOERR) CALL nc_abort &
                (ok,'Error finding land dimension in ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           ok = NF90_INQUIRE_DIMENSION(ncid_met,landdimID,len=mland_fromfile)
           IF(ok/=NF90_NOERR) CALL nc_abort &
                (ok,'Error determining size of land dimension in ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           ! Allocate landGrid variable and its temporary counterpart:
           ALLOCATE(landGrid(mland_fromfile))
           ALLOCATE(temparray1(mland_fromfile))
           ! Get values of "land" variable from file:
           ok= NF90_GET_VAR(ncid_met,landID,temparray1)
           IF(ok /= NF90_NOERR) CALL nc_abort &
                (ok,'Error reading "land" variable in ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           ! Needed since r_1 will be double precision with -r8:
           landGrid = REAL(temparray1)
           DEALLOCATE(temparray1)
           ! Allocate latitude and longitude variables:
           ALLOCATE(latitude(mland_fromfile),longitude(mland_fromfile))
           ! Write to indicies of points in all-grid which are land
           ALLOCATE(land_x(mland_fromfile),land_y(mland_fromfile))
           ! Allocate "mask" variable:
           ALLOCATE(mask(xdimsize,ydimsize))
           ! Initialise all gridpoints as sea:
           mask = 0
           DO j=1, mland_fromfile ! over all land points
              ! Find x and y coords of current land point
              y = INT((landGrid(j)-1)/xdimsize)
              x = landGrid(j) - y * xdimsize
              y=y+1
              ! Write lat and lon to land-only lat/lon vars:
              latitude(j) = lat_all(x,y)
              longitude(j) = lon_all(x,y)
              ! Write to mask variable:
              mask(x,y)=1
              ! Save indicies:
              land_x(j) = x
              land_y(j) = y
           END DO
        END IF ! does "land" variable exist
     ELSE ! i.e. "mask" variable exists
        ! Allocate "mask" variable:
        ALLOCATE(mask(xdimsize,ydimsize))
        metGrid='mask' ! Use mask system
        ! Get mask values from file:
        ok= NF90_GET_VAR(ncid_mask,maskID,mask)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error reading "mask" variable in ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        !gswp3 uses 1 for sea and 0 for land, make is opposite
        IF (cable_user%gswp3) mask = 1-mask
 
        ! Allocate space for extracting land lat/lon values:
        ALLOCATE(lat_temp(ngridcells),lon_temp(ngridcells))
        ! Allocate space for extracting index of mask which is land
        ALLOCATE(land_xtmp(ngridcells),land_ytmp(ngridcells))
        ! Cycle through all gridsquares:
        mland_ctr = 0 ! initialise
        DO y=1,ydimsize
           DO x=1,xdimsize
              IF(mask(x,y)==1) THEN ! If land
                 mland_ctr = mland_ctr + 1
                 ! Store lat and lon for land points
                 lat_temp(mland_ctr) = lat_all(x,y)
                 lon_temp(mland_ctr) = lon_all(x,y)
                 ! Store indicies of points in mask which are land
                 land_xtmp(mland_ctr) = x
                 land_ytmp(mland_ctr) = y
              END IF
           END DO
        END DO
        ! Record number of land points
        mland_fromfile = mland_ctr
        ! Allocate latitude and longitude variables:
        ALLOCATE(latitude(mland_fromfile),longitude(mland_fromfile))
        ! Write to latitude and longitude variables:
        latitude = lat_temp(1:mland_fromfile)
        longitude = lon_temp(1:mland_fromfile)
        ! Write to indicies of points in mask which are land
        ALLOCATE(land_x(mland_fromfile),land_y(mland_fromfile))
        land_x = land_xtmp(1:mland_fromfile)
        land_y = land_ytmp(1:mland_fromfile)
        ! Clear lon_temp, lat_temp,land_xtmp,land_ytmp
        DEALLOCATE(lat_temp,lon_temp,land_xtmp,land_ytmp)
     END IF ! "mask" variable or no "mask" variable
 
     ! Set global mland value (number of land points), used to allocate
     ! all of CABLE's arrays:
     mland = mland_fromfile
 
     ! Write number of land points to log file:
     WRITE(logn,'(24X,I7,A29)') mland_fromfile, ' of which are land grid cells'
 
     ! Check if veg/soil patch dimension exists (could have
     ! parameters with patch dimension)
     ok = NF90_INQ_DIMID(ncid_met,'patch', patchdimID)
     IF(ok/=NF90_NOERR) THEN ! if failed
        exists%patch = .FALSE.
        nmetpatches = 1       ! initialised so that old met files without patch
        ! data can still be run correctly (BP apr08)
     ELSE ! met file does have patch dimension
        exists%patch = .TRUE.
        ok = NF90_INQUIRE_DIMENSION(ncid_met,patchdimID,len=nmetpatches)
     END IF
 
     ! Check if monthly dimension exists for LAI info
     ok = NF90_INQ_DIMID(ncid_met,'monthly', monthlydimID)
     IF(ok==NF90_NOERR) THEN ! if found
        ok = NF90_INQUIRE_DIMENSION(ncid_met,monthlydimID,len=tempmonth)
        IF(tempmonth/=12) CALL abort ('Number of months in met file /= 12.')
     END IF
 
     ! Set longitudes to be [-180,180]:
     WHERE(longitude>180.0)
        longitude = longitude - 360.0
     END WHERE
 
     ! Check ranges for latitude and longitude:
     IF(ANY(longitude>180.0).OR.ANY(longitude<-180.0)) &
          CALL abort('Longitudes read from '//TRIM(filename%met)// &
          ' are not [-180,180] or [0,360]! Please set.')
     IF(ANY(latitude>90.0).OR.ANY(latitude<-90.0)) &
          CALL abort('Latitudes read from '//TRIM(filename%met)// &
          ' are not [-90,90]! Please set.')
 
     !!=================^^ End spatial details ^^========================
 
     !!=========VV Determine simulation timing details VV================
     ! Inquire 'time' variable's ID:
     ok = NF90_INQ_VARID(ncid_met, 'time', timevarID)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding time variable in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Get ID for dimension upon which time depends:
     ok = NF90_INQUIRE_VARIABLE(ncid_met,timevarID,dimids=timedimID)
     IF(ok/=NF90_NOERR) CALL nc_abort &
          (ok,'Error determining "time" dimension dimension in ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Determine number of time steps:
     ok = NF90_INQUIRE_DIMENSION(ncid_met,timedimID(1),len=kend)
     IF(ok/=NF90_NOERR) CALL nc_abort &
          (ok,'Error determining number of timesteps in ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Allocate time variable:
     ALLOCATE(timevar(kend))
     ! Fetch 'time' variable:
     ok= NF90_GET_VAR(ncid_met,timevarID,timevar)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error reading time variable in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     IF (cable_user%gswp3) then         !Hack the GSWP3 time units to make from start of year
        timevar(:) = (timevar(:)-timevar(1))*3600.0 + 1.5*3600.0  !convert hours to seconds
     end if
     ! Set time step size:
     dels = REAL(timevar(2) - timevar(1))
     WRITE(logn,'(1X,A29,I8,A3,F10.3,A5)') 'Number of time steps in run: ',&
          kend,' = ', REAL(kend)/(3600/dels*24),' days'
 
 
     ! CLN READJUST kend referring to Set START & END
     ! if kend > # days in selected episode
 
 
     !********* gswp input file has bug in timevar **************
     IF (ncciy > 0) THEN
       PRINT *, 'original timevar(kend) = ', timevar(kend)
       DO i = 1, kend - 1
         timevar(i+1) = timevar(i) + dels
       ENDDO
       PRINT *, 'New      timevar(kend) = ', timevar(kend)
 !! hacking (BP feb2011)
 !      kend = 16   ! 2 days for 1986
 !!      kend = 480  ! 2 months for 1986
 !      PRINT *, 'Hacked   timevar(kend) = ', timevar(kend)
 !      PRINT *, 'Hacked kend = ', kend
 !! end hacking
     END IF
     !********* done bug fixing for timevar in gswp input file **
 
     ! Write time step size to log file:
     WRITE(logn,'(1X,A17,F8.1,1X,A7)') 'Time step size:  ', dels, 'seconds'
     ! Get units for 'time' variable:
     ok = NF90_GET_ATT(ncid_met,timevarID,'units',timeunits)
     if (.not.cable_user%GSWP3) then
        ok = NF90_GET_ATT(ncid_met,timevarID,'units',timeunits)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding time variable units in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     else
        !Hack the GSWP3 time units to make from start of year
        write(*,*) 'writing timeunits'
        write (timeunits, "('seconds since ',I4.4,'-01-01 00:00:00')") ncciy
        write(*,*) 'wrote time units'
     end if
     !MDeck
     !write(*,*) timeunits
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding time variable units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
 
     !****** PALS met file has timevar(1)=0 while timeunits from 00:30:00 ******
     !!CLN CRITICAL! From my point of view, the information in the file is correct...
     !!CLN WHY DO the input files all have bugs???
     IF (timevar(1) == 0.0) THEN
       READ(timeunits(29:30),*) tsmin
       IF (tsmin*60.0 >= dels) THEN
         tsmin = tsmin - INT(dels / 60)
         timevar = timevar + dels
         WRITE(timeunits(29:30),'(i2.2)') tsmin
       ENDIF
     ENDIF
     !****** done bug fixing for timevar in PALS met file **********************
 
     !********* gswp input file has bug in timeunits ************
     IF (ncciy > 0) WRITE(timeunits(26:27),'(i2.2)') 0
     !********* done bug fixing for timeunits in gwsp file ******
     WRITE(logn,*) 'Time variable units: ', timeunits
     ! Get coordinate field:
     ok = NF90_GET_ATT(ncid_met,timevarID,'coordinate',time_coord)
     ! If error getting coordinate field (i.e. it doesn't exist):
     IF(ok /= NF90_NOERR) THEN
        ! Assume default time coordinate:
        IF(mland_fromfile==1.and.(TRIM(cable_user%MetType) .NE. 'gswp')) THEN ! If single site, this is local time
           time_coord = 'LOC' ! 12am is 12am local time, at site/gridcell
        ELSE ! If multiple/global/regional, use GMT
           time_coord = 'GMT' ! 12am is GMT time, local time set by longitude
        END IF
     ELSE IF((ok==NF90_NOERR.AND.time_coord=='LOC'.AND.mland_fromfile>1)) THEN
        ! Else if local time is selected for regional simulation, abort:
        CALL abort('"time" variable must be GMT for multiple site simulation!' &
             //' Check "coordinate" field in time variable.' &
             //' (SUBROUTINE open_met_file)')
     ELSE IF(time_coord/='LOC'.AND.time_coord/='GMT') THEN
        CALL abort('Meaningless time coordinate in met data file!' &
             // ' (SUBROUTINE open_met_file)')
     END IF
 
     ! Use internal files to convert "time" variable units (giving the run's
     ! start time) from character to integer; calculate starting hour-of-day,
     ! day-of-year, year:
     IF (.not.cable_user%GSWP3) then 
        READ(timeunits(15:18),*) syear
        READ(timeunits(20:21),*) smoy ! integer month
        READ(timeunits(23:24),*) sdoytmp ! integer day of that month
        READ(timeunits(26:27),*) shod  ! starting hour of day 
     ELSE 
        syear=ncciy
        smoy=1
        sdoytmp=1
        shod=0
     END IF
     ! if site data, shift start time to middle of timestep
     ! only do this if not already at middle of timestep
     !! vh_js !!
     IF (TRIM(cable_user%MetType).EQ.'' .and. MOD(shod*3600, dels)==0 .and. &
          (shod.gt.dels/3600./2.) ) THEN
        shod = shod - dels/3600./2.
     ELSEIF (TRIM(cable_user%MetType).EQ.'' .and. MOD(shod*3600, dels)==0 .and. &
          (shod.lt.dels/3600./2.) ) THEN
        shod = shod + dels/3600./2.
     ENDIF
     
    
     ! Decide day-of-year for non-leap year:
     CALL YMDHMS2DOYSOD( syear, smoy, sdoytmp, INT(shod), 0, 0, sdoy, ssod )
        ! Number of days between start position and 1st timestep:
     sdoy = sdoy + INT((timevar(1)/3600.0 + shod)/24.0)
     nsod = MOD(INT((timevar(1) + shod*3600)),86400)
 
     DO
        LOY = 365
        IF ( IS_LEAPYEAR( syear ) ) LOY = 366
        IF ( sdoy .GT. LOY ) THEN
           sdoy  = sdoy - LOY
           syear = syear + 1
        ELSE
           EXIT
        END IF
     END DO
 
 
     CALL DOYSOD2YMDHMS( syear, sdoy, nsod, smoy, iday, ishod, imin, isec )
     shod = REAL(ishod) + REAL(imin)/60. + REAL(isec)/3600.
     ! Cycle through days to find leap year inclusive starting date:
     ! Now all start time variables established, report to log file:
     WRITE(logn,'(1X,A12,F5.2,A14,I3,A14,I4,2X,A3,1X,A4)') &
          'Run begins: ',shod,' hour-of-day, ',sdoy, ' day-of-year, ',&
          syear, time_coord, 'time'
     ! Determine ending time of run...
     IF(leaps) THEN ! If we're using leap year timing...
        eyear = syear
        edoy  = sdoy + INT(((timevar(kend)-timevar(1))/3600.0 + shod)/24.0)
        ehod  = MOD(((timevar(kend)-timevar(1)/3600.) + shod),24._r_2)
 
        DO
           LOY = 365
           IF ( IS_LEAPYEAR( eyear ) ) LOY = 366
           IF ( edoy .GT. LOY ) THEN
              edoy  = edoy - LOY
                 eyear = eyear + 1
           ELSE
              EXIT
           END IF
        END DO
 
 
     ELSE ! if not using leap year timing
        ! Update shod, sdoy, syear for first "time" value:
        ehod = MOD(REAL((timevar(kend)-timevar(1))/3600.0 + shod),24.0)
        edoy = MOD(INT(((timevar(kend)-timevar(1))/3600.0 + shod)/24.0) &
             + sdoy, 365)
        eyear = INT(REAL(INT(((timevar(kend)-timevar(1)) &
             /3600.0+shod)/24.0)+sdoy)/365.0)+syear
 !       ehod = MOD(REAL((timevar(kend)-timevar(1)+dels)/3600.0 + shod),24.0)
 !       edoy = MOD(INT(((timevar(kend)-timevar(1)+dels)/3600.0 + shod)/24.0) &
 !            + sdoy, 365)
 !       eyear = INT(REAL(INT(((timevar(kend)-timevar(1)+dels) &
 !            /3600.0+shod)/24.0)+sdoy)/365.0)+syear
     END IF
     ! IF A CERTAIN PERIOD IS DESIRED AND WE ARE NOT RUNNING ON GSWP DATA
     ! RECALCULATE STARTING AND ENDING INDICES
     IF ( CABLE_USER%YEARSTART .GT. 0 .AND. .NOT. ncciy.GT.0) THEN
        IF ( syear.GT.CABLE_USER%YEARSTART .OR. eyear.LE.CABLE_USER%YEAREND .OR. &
             ( syear.EQ.CABLE_USER%YEARSTART .AND. sdoy.gt.1 ) ) THEN
           WRITE(*,*) "Chosen period doesn't match dataset period!"
           WRITE(*,*) "Chosen period: ",CABLE_USER%YEARSTART,1,CABLE_USER%YEAREND,365
           WRITE(*,*) "Data   period: ",syear,sdoy, eyear,edoy
           WRITE(*,*) "For using the metfile's time set CABLE_USER%YEARSTART = 0 !"
           STOP
        ENDIF
 
        ! Find real kstart!
        dnsec = 0
        DO y = syear, CABLE_USER%YEARSTART-1
           LOY = 365
           IF ( IS_LEAPYEAR( y ) ) LOY = 366
           IF ( y .EQ. syear ) THEN
              dnsec = ( LOY - sdoy ) * 86400 + (24 - shod) * 3600
           ELSE
              dnsec = dnsec + LOY * 86400
           ENDIF
        END DO
        koffset = INT(REAL(dnsec)/REAL(dels)) - 1
        ! Find real kend
        kend = 0
        DO y = CABLE_USER%YEARSTART, CABLE_USER%YEAREND
           LOY = 365
           IF ( IS_LEAPYEAR( y ) ) LOY = 366
           kend = kend + INT( REAL(LOY) * 86400./REAL(dels) )
        END DO
     ENDIF
 
     ! Report finishing time to log file:
     WRITE(logn,'(1X,A12,F5.2,A14,I3,A14,I4,2X,A3,1X,A4)') 'Run ends:   ',&
          ehod,' hour-of-day, ',edoy, &
          ' day-of-year, ', eyear, time_coord, 'time'
     !!===================^^ End timing details ^^==========================
 
     !!===================VV Look for met variables VV======================
     all_met = .TRUE. ! initialise
     ! Look for SWdown (essential):- - - - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_sw
     ok = NF90_INQ_VARID(ncid_met,'SWdown',id%SWdown)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding SWdown in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Get SWdown units and check okay:
     ok = NF90_GET_ATT(ncid_met,id%SWdown,'units',metunits%SWdown)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding SWdown units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
   !! vh_js !! fixed bug in logic
     IF(.NOT.(metunits%SWdown(1:4)/='W/m2'.OR.metunits%SWdown(1:5) &
          /='W/m^2'.OR.metunits%SWdown(1:5)/='Wm^-2' &
          .OR.metunits%SWdown(1:4)/='Wm-2'.or.metunits%SWdown(1:5) /= 'W m-2')) THEN
        WRITE(*,*) metunits%SWdown
        CALL abort('Unknown units for SWdown'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     END IF
     ! Look for Tair (essential):- - - - - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_ta
     ok = NF90_INQ_VARID(ncid_met,'Tair',id%Tair)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Tair in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Get Tair units and check okay:
     ok = NF90_GET_ATT(ncid_met,id%Tair,'units',metunits%Tair)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Tair units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     IF(metunits%Tair(1:1)=='C'.OR.metunits%Tair(1:1)=='c') THEN
        ! Change from celsius to kelvin:
        convert%Tair = tfrz
        WRITE(logn,*) 'Temperature will be converted from C to K'
     ELSE IF(metunits%Tair(1:1)=='K'.OR.metunits%Tair(1:1)=='k') THEN
        ! Units are correct
        convert%Tair = 0.0
     ELSE
        WRITE(*,*) metunits%Tair
        CALL abort('Unknown units for Tair'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     END IF
     ! Look for Qair (essential):- - - - - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_qa
     ok = NF90_INQ_VARID(ncid_met,'Qair',id%Qair)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Qair in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     ! Get Qair units:
     ok = NF90_GET_ATT(ncid_met,id%Qair,'units',metunits%Qair)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Qair units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     IF(metunits%Qair(1:1)=='%'.OR.metunits%Qair(1:1)=='-') THEN
        ! Change from relative humidity to specific humidity:
        convert%Qair = -999.0
        WRITE(logn,*) 'Humidity will be converted from relative to specific'
     ELSE IF(metunits%Qair(1:3)=='g/g'.OR.metunits%Qair(1:5)=='kg/kg' &
          .OR.metunits%Qair(1:3)=='G/G'.OR.metunits%Qair(1:5)=='KG/KG'.or.metunits%Qair(1:7)=='kg kg-1') THEN
        ! Units are correct
        convert%Qair=1.0
     ELSE
        WRITE(*,*) metunits%Qair
        CALL abort('Unknown units for Qair'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     END IF
     ! Look for Rainf (essential):- - - - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_rain
     ok = NF90_INQ_VARID(ncid_met,'Rainf',id%Rainf)
     IF(ok /= NF90_NOERR) THEN
         ok = NF90_INQ_VARID(ncid_met,'Precip',id%Rainf)
         IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Rainf in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     END IF
     ! Get Rainf units:
     ok = NF90_GET_ATT(ncid_met,id%Rainf,'units',metunits%Rainf)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Rainf units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     IF(metunits%Rainf(1:8)=='kg/m^2/s'.OR.metunits%Rainf(1:6)=='kg/m2s'.OR.metunits%Rainf(1:10)== &
          'kgm^-2s^-1'.OR.metunits%Rainf(1:4)=='mm/s'.OR. &
          metunits%Rainf(1:6)=='mms^-1'.OR. &
          metunits%Rainf(1:7)=='kg/m^2s'.or.metunits%Rainf(1:10)=='kg m-2 s-1'.or.metunits%Wind(1:5)/='m s-1') THEN
        ! Change from mm/s to mm/time step:
         convert%Rainf = dels
     ELSE IF(metunits%Rainf(1:4)=='mm/h'.OR.metunits%Rainf(1:6)== &
          'mmh^-1') THEN
        ! Change from mm/h to mm/time step:
        convert%Rainf = dels/3600.0
     ELSE
        WRITE(*,*) metunits%Rainf
        CALL abort('Unknown units for Rainf'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     END IF
     ! Multiply acceptable Rainf ranges by time step size:
     !ranges%Rainf = ranges%Rainf*dels ! range therefore depends on dels ! vh ! why has this been commented out?
     ranges%Rainf = ranges%Rainf*dels ! range therefore depends on dels
     ! Look for Wind (essential):- - - - - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_wd
     ok = NF90_INQ_VARID(ncid_met,'Wind',id%Wind)
     IF(ok /= NF90_NOERR) THEN
        ! Look for vector wind:
        ok = NF90_INQ_VARID(ncid_met,'Wind_N',id%Wind)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding Wind in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        ok = NF90_INQ_VARID(ncid_met,'Wind_E',id%Wind_E)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding Wind_E in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        exists%Wind = .FALSE. ! Use vector wind when reading met
     ELSE
        exists%Wind = .TRUE. ! 'Wind' variable exists
     END IF
     ! Get Wind units:
     ok = NF90_GET_ATT(ncid_met,id%Wind,'units',metunits%Wind)
     IF(ok /= NF90_NOERR) CALL nc_abort &
          (ok,'Error finding Wind units in met data file ' &
          //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
     IF (metunits%Wind(1:3)/='m/s'.AND.metunits%Wind(1:2)/='ms'.AND.metunits%Wind(1:5)/='m s-1') THEN
        WRITE(*,*) metunits%Wind
        CALL abort('Unknown units for Wind'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     END IF
     ! Now "optional" variables:
     ! Look for LWdown (can be synthesised):- - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_lw
     ok = NF90_INQ_VARID(ncid_met,'LWdown',id%LWdown)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        exists%LWdown = .TRUE. ! LWdown is present in met file
        ! Get LWdown units and check okay:
        ok = NF90_GET_ATT(ncid_met,id%LWdown,'units',metunits%LWdown)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding LWdown units in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
  !! vh_js !! fixed bug in logic
 !!$       IF(metunits%LWdown(1:4)/='W/m2'.AND.metunits%LWdown(1:5) &
 !!$            /='W/m^2'.AND.metunits%LWdown(1:5)/='Wm^-2' &
 !!$            .AND.metunits%LWdown(1:4)/='Wm-2') THEN
        IF(.NOT.(metunits%LWdown(1:4)/='W/m2'.OR.metunits%LWdown(1:5) &
             /='W/m^2'.OR.metunits%LWdown(1:5)/='Wm^-2' &
             .OR.metunits%LWdown(1:4)/='Wm-2'.or.metunits%SWdown(1:5) /= 'W m-2')) THEN
 
           WRITE(*,*) metunits%LWdown
           CALL abort('Unknown units for LWdown'// &
                ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
        END IF
     ELSE
        exists%LWdown = .FALSE. ! LWdown is not present in met file
        all_met=.FALSE. ! not all met variables are present in file
        ! Note this in log file:
        WRITE(logn,*) 'LWdown not present in met file; ', &
             'values will be synthesised based on air temperature.'
     END IF
     ! Look for PSurf (can be synthesised):- - - - - - - - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_ps
     ok = NF90_INQ_VARID(ncid_met,'PSurf',id%PSurf)
     IF (ok /= NF90_NOERR)  & ! Try alternate name
      ok = NF90_INQ_VARID(ncid_met,'Psurf',id%PSurf)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        exists%PSurf = .TRUE. ! PSurf is present in met file
        ! Get PSurf units and check:
        ok = NF90_GET_ATT(ncid_met,id%PSurf,'units',metunits%PSurf)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding PSurf units in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        IF(metunits%PSurf(1:2)=='Pa'.OR.metunits%PSurf(1:2)=='pa'.OR. &
             metunits%PSurf(1:2)=='PA' ) THEN
           ! Change from pa to mbar (cable uses mbar):
           convert%PSurf = 0.01
           WRITE(logn,*) 'Pressure will be converted from Pa to mb'
        ELSE IF(metunits%PSurf(1:2)=='KP'.OR.metunits%PSurf(1:2)=='kP' &
             .OR.metunits%PSurf(1:2)=='Kp'.OR.metunits%PSurf(1:2)=='kp') THEN
           ! convert from kPa to mb
           convert%PSurf = 10.0
           WRITE(logn,*) 'Pressure will be converted from kPa to mb'
        ELSE IF(metunits%PSurf(1:2)=='MB'.OR.metunits%PSurf(1:2)=='mB' &
             .OR.metunits%PSurf(1:2)=='Mb'.OR.metunits%PSurf(1:2)=='mb') THEN
           ! Units are correct
           convert%PSurf = 1.0
        ELSE
           WRITE(*,*) metunits%PSurf
           CALL abort('Unknown units for PSurf'// &
                ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
        END IF
     ELSE ! If PSurf not present
        exists%PSurf = .FALSE. ! PSurf is not present in met file
        all_met=.FALSE. ! not all met variables are present in file
        ! Look for "elevation" variable to approximate pressure based
        ! on elevation and temperature:
        ok = NF90_INQ_VARID(ncid_met,'Elevation',id%Elev)
        IF(ok == NF90_NOERR) THEN ! elevation present
           ! Get elevation units:
           ok = NF90_GET_ATT(ncid_met,id%Elev,'units',metunits%Elev)
           IF(ok /= NF90_NOERR) CALL nc_abort &
                (ok,'Error finding elevation units in met data file ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           ! Units should be metres or feet:
           IF(metunits%Elev(1:1)=='m'.OR.metunits%Elev(1:1)=='M') THEN
              ! This is the expected unit - metres
              convert%Elev = 1.0
           ELSE IF(metunits%Elev(1:1)=='f'.OR.metunits%Elev(1:1)=='F') THEN
              ! Convert from feet to metres:
              convert%Elev = 0.3048
           ELSE
              CALL abort('Unknown units for Elevation'// &
                   ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
           END IF
           ! Allocate space for elevation variable:
           ALLOCATE(elevation(mland))
           ! Get site elevations:
           IF(metGrid=='mask') THEN
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%Elev,data2, &
                      start=(/land_x(i),land_y(i)/),count=(/1,1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading elevation in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 elevation(i)=REAL(data2(1,1))*convert%Elev
              END DO
           ELSE IF(metGrid=='land') THEN
              ! Collect data from land only grid in netcdf file:
              ok= NF90_GET_VAR(ncid_met,id%Elev,data1)
              IF(ok /= NF90_NOERR) CALL nc_abort &
                   (ok,'Error reading elevation in met data file ' &
                   //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              elevation = REAL(data1) * convert%Elev
           END IF
        ELSE ! If both PSurf and elevation aren't present, abort:
           CALL abort &
                ('Error finding PSurf or Elevation in met data file ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        END IF
        ! Note static pressure based on elevation in log file:
        WRITE(logn,*) 'PSurf not present in met file; values will be ', &
             'synthesised based on elevation and temperature.'
     END IF
     ! Look for CO2air (can be assumed to be static):- - - - - - - - - - -
     ok = NF90_INQ_VARID(ncid_met,'CO2air',id%CO2air)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        exists%CO2air = .TRUE. ! CO2air is present in met file
        ! Get CO2air units:
        ok = NF90_GET_ATT(ncid_met,id%CO2air,'units',metunits%CO2air)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding CO2air units in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        IF(metunits%CO2air(1:3)/='ppm') THEN
           WRITE(*,*) metunits%CO2air
           CALL abort('Unknown units for CO2air'// &
                ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
        END IF
     ELSE ! CO2 not present
        exists%CO2air = .FALSE. ! CO2air is not present in met file
        all_met=.FALSE. ! not all met variables are present in file
        ! Note this in log file:
        WRITE(logn,'(A33,A24,I4,A5)') ' CO2air not present in met file; ', &
             'values will be fixed at ',INT(fixedCO2),' ppmv'
     END IF
     ! Look for Snowf (could be part of Rainf variable):- - - - - - - - - -
     IF (ncciy > 0) ncid_met = ncid_snow
     ok = NF90_INQ_VARID(ncid_met,'Snowf',id%Snowf)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        exists%Snowf = .TRUE. ! Snowf is present in met file
        ! Get Snowf units:
        ok = NF90_GET_ATT(ncid_met,id%Snowf,'units',metunits%Snowf)
        IF(ok /= NF90_NOERR) CALL nc_abort &
             (ok,'Error finding Snowf units in met data file ' &
             //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
        ! Make sure Snowf units are the same as Rainf units:
        IF(metunits%Rainf/=metunits%Snowf) CALL abort &
             ('Please ensure Rainf and Snowf units are the same'// &
             ' in '//TRIM(filename%met)//' (SUBROUTINE open_met_data)')
     ELSE
        exists%Snowf = .FALSE. ! Snowf is not present in met file
        !  all_met=.FALSE. not required; Snowf assumed to be in Rainf
        ! Note this in log file:
        WRITE(logn,*) 'Snowf not present in met file; ', &
             'Assumed to be contained in Rainf variable'
     END IF
     ! Look for LAI - - - - - - - - - - - - - - - - - - - - - - - - -
     ok = NF90_INQ_VARID(ncid_met,'LAI',id%LAI)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        exists%LAI = .TRUE. ! LAI is present in met file
        ! LAI will be read in which ever land grid is used
        ! Check dimension of LAI variable:
        ok=NF90_INQUIRE_VARIABLE(ncid_met,id%LAI, &
             ndims=lai_dims,dimids=laidimids)
        ! If any of LAI's dimensions are the time dimension
        IF(ANY(laidimids==timedimID(1))) THEN
           exists%LAI_T = .TRUE. ! i.e. time varying LAI
           WRITE(logn,*) 'LAI found in met file - time dependent;'
        ELSE
           exists%LAI_T = .FALSE. ! i.e. not time varying LAI
        END IF
        IF(ANY(laidimids==monthlydimID)) THEN
           exists%LAI_M = .TRUE. ! i.e. time varying LAI, but monthly only
           WRITE(logn,*) 'LAI found in met file - monthly values;'
        ELSE
           exists%LAI_M = .FALSE.
        END IF
        IF(ANY(laidimids==patchdimID)) THEN
           exists%LAI_P = .TRUE. ! i.e. patch varying LAI
           WRITE(logn,*) 'LAI found in met file - patch-specific values'
        ELSE
           exists%LAI_P = .FALSE. ! i.e. not patch varying LAI
        END IF
     ELSE
        exists%LAI = .FALSE. ! LAI is not present in met file
        ! Report to log file
        WRITE(logn,*) 'LAI not present in met file; ', &
             'Will use MODIS coarse grid monthly LAI'
     END IF
     ! If a spinup is to be performed:
     IF(spinup) THEN
        ! Look for avPrecip variable (time invariant - used for spinup):
        ok = NF90_INQ_VARID(ncid_met,'avPrecip',id%avPrecip)
        IF(ok == NF90_NOERR) THEN ! If inquiry is okay and avPrecip exists
           ! Report to log file than modified spinup will be used:
           WRITE(logn,*) 'Spinup will use modified precip - avPrecip variable found'
           WRITE(logn,*) '  precip will be rescaled to match these values during spinup:'
           WRITE(*,*) 'Spinup will use modified precip - avPrecip variable found'
           WRITE(*,*) '  precip will be rescaled to match these values during spinup'
           ! Spinup will modify precip values:
           exists%avPrecip = .TRUE.
           ! Get avPrecip units:
           ok = NF90_GET_ATT(ncid_met,id%avPrecip,'units',metunits%avPrecip)
           IF(ok /= NF90_NOERR) CALL nc_abort &
                (ok,'Error finding avPrecip units in met data file ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           IF(metunits%avPrecip(1:2)/='mm') CALL abort( &
                'Unknown avPrecip units in met data file ' &
                //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
           ! Allocate space for avPrecip variable:
           ALLOCATE(avPrecip(mland))
           ! Get avPrecip from met file:
           IF(metGrid=='mask') THEN
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%avPrecip,data2, &
                      start=(/land_x(i),land_y(i)/),count=(/1,1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading avPrecip in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 avPrecip(i)=REAL(data2(1,1))
              END DO
           ELSE IF(metGrid=='land') THEN
              ! Allocate single preciaion temporary variable:
              ALLOCATE(temparray1(mland))
              ! Collect data from land only grid in netcdf file:
              ok= NF90_GET_VAR(ncid_met,id%avPrecip,temparray1)
              IF(ok /= NF90_NOERR) CALL nc_abort &
                   (ok,'Error reading avPrecip in met data file ' &
                   //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              ! Needed since r_1 will be double precision with -r8:
              avPrecip = REAL(temparray1)
              DEALLOCATE(temparray1)
           END IF
           ! Now find average precip from met data, and create rescaling
           ! factor for spinup:
           ALLOCATE(PrecipScale(mland))
           DO i = 1, mland
              IF(metGrid=='mask') THEN
                 ! Allocate space for temporary precip variable:
                 ALLOCATE(tempPrecip3(1,1,kend))
                 ! Get all data for this grid cell:
                 ok= NF90_GET_VAR(ncid_met,id%Rainf,tempPrecip3, &
                      start=(/land_x(i),land_y(i),1+koffset/),count=(/1,1,kend/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading Rainf in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Store total Rainf for this grid cell:
                 PrecipTot = REAL(SUM(SUM(SUM(tempPrecip3,3),2))) &
                      * convert%Rainf
                 ! Get snowfall data for this grid cell:
                 IF(exists%Snowf) THEN
                    ok= NF90_GET_VAR(ncid_met,id%Snowf,tempPrecip3, &
                         start=(/land_x(i),land_y(i),1+koffset/),count=(/1,1,kend/))
                    IF(ok /= NF90_NOERR) CALL nc_abort &
                         (ok,'Error reading Snowf in met data file ' &
                         //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                    ! Add total Snowf to this grid cell total:
                    PrecipTot = PrecipTot + &
                         (REAL(SUM(SUM(SUM(tempPrecip3,3),2))) &
                         * convert%Rainf)
                 END IF
                 DEALLOCATE(tempPrecip3)
              ELSE IF(metGrid=='land') THEN
                 ! Allocate space for temporary precip variable:
                 ALLOCATE(tempPrecip2(1,kend))
                 ! Get rainfall data for this land grid cell:
                 ok= NF90_GET_VAR(ncid_met,id%Rainf,tempPrecip2, &
                      start=(/i,1+koffset/),count=(/1,kend/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading Rainf in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Store total Rainf for this land grid cell:
                 PrecipTot = REAL(SUM(SUM(tempPrecip2,2)))*convert%Rainf
                 IF(exists%Snowf) THEN
                    ok= NF90_GET_VAR(ncid_met,id%Snowf,tempPrecip2, &
                         start=(/i,1+koffset/),count=(/1,kend/))
                    IF(ok /= NF90_NOERR) CALL nc_abort &
                         (ok,'Error reading Snowf in met data file ' &
                         //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                    ! Add total Snowf to this land grid cell total:
                    PrecipTot = PrecipTot + (REAL(SUM(SUM(tempPrecip2,2))) &
                         * convert%Rainf)
                 END IF
                 DEALLOCATE(tempPrecip2)
              END IF
              ! Create rescaling factor for this grid cell to ensure spinup
              ! rainfall/snowfall is closer to average rainfall:
              ! First calculate annual average precip in met data:
              avPrecipInMet = PrecipTot/REAL(kend) * 3600.0/dels * 365 * 24
              PrecipScale(i) = avPrecipInMet/avPrecip(i)
              WRITE(logn,*) '  Site number:',i
              WRITE(logn,*) '  average precip quoted in avPrecip variable:', &
                   avPrecip(i)
              WRITE(logn,*) '  average precip in met data:',avPrecipInMet
           END DO ! over each land grid cell
           DEALLOCATE(avPrecip)
        ELSE ! avPrecip doesn't exist in met file
           ! Spinup will not modify precip values:
           exists%avPrecip = .FALSE.
           WRITE(logn,*) 'Spinup will repeat entire data set until states converge'
           WRITE(logn,*) '  (see below for convergence criteria);'
           WRITE(*,*) 'Spinup will repeat entire data set until states converge:'
        END IF
     END IF  ! if a spinup is to be performed
 
     ! Look for veg type - - - - - - - - - - - - - - - - -:
     ok = NF90_INQ_VARID(ncid_met,'iveg',id%iveg)
     IF(ok == NF90_NOERR) THEN ! If 'iveg' exists in the met file
        ! Note existence of at least one model parameter in the met file:
        exists%parameters = .TRUE.
        ! Allocate space for user-defined veg type variable:
        ALLOCATE(vegtype_metfile(mland,nmetpatches))
        ! Check dimension of veg type:
        ok=NF90_INQUIRE_VARIABLE(ncid_met,id%iveg,ndims=iveg_dims)
        IF(metGrid=='mask') THEN ! i.e. at least two spatial dimensions
           IF(iveg_dims==2) THEN ! no patch specific iveg information, just x,y
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%iveg,data2i, & ! get iveg data
                      start=(/land_x(i),land_y(i)/),count=(/1,1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading iveg in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Set all veg patches in grid cell to be this single type
                 vegtype_metfile(i,:)=data2i(1,1)
              END DO
           ELSE IF(iveg_dims==3) THEN ! i.e. patch specific iveg information
              ! Patch-specific iveg variable MUST be accompanied by
              ! patchfrac variable with the same dimensions. So,
              ! Make sure that the patchfrac variable exists:
              ok = NF90_INQ_VARID(ncid_met,'patchfrac',id%patchfrac)
              IF(ok /= NF90_NOERR) CALL nc_abort & ! check read ok
                   (ok,'Patch-specific vegetation type (iveg) must be accompanied '// &
                   'by a patchfrac variable - this was not found in met data file '&
                   //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              DO i = 1, mland
                 ! Then, get the patch specific iveg data:
                 ok= NF90_GET_VAR(ncid_met,id%iveg,vegtype_metfile(i,:), &
                      start=(/land_x(i),land_y(i),1/),count=(/1,1,nmetpatches/))
                 IF(ok /= NF90_NOERR) CALL nc_abort & ! check read ok
                      (ok,'Error reading iveg in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              END DO
           END IF
        ELSE IF(metGrid=='land') THEN
           ! Collect data from land only grid in netcdf file:
           IF(iveg_dims==1) THEN ! i.e. no patch specific iveg information
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%iveg,data1i, &
                      start=(/i/),count=(/1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading iveg in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Set all veg patches in grid cell to be this single type
                 vegtype_metfile(i,:) = data1i(1)
              END DO
           ELSE IF(iveg_dims==2) THEN ! i.e. patch specific iveg information
              ! Patch-specific iveg variable MUST be accompanied by
              ! patchfrac variable with same dimensions. So,
              ! Make sure that the patchfrac variable exists:
              ok = NF90_INQ_VARID(ncid_met,'patchfrac',id%patchfrac)
              IF(ok /= NF90_NOERR) CALL nc_abort & ! check read ok
                   (ok,'Patch-specific vegetation type (iveg) must be accompanied'// &
                   'by a patchfrac variable - this was not found in met data file '&
                   //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              DO i = 1, mland
                 ! Then, get the patch specific iveg data:
                 ok= NF90_GET_VAR(ncid_met, id%iveg, &
                      vegtype_metfile(i,:),&
                      start=(/i,1/), count=(/1,nmetpatches/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading iveg in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              END DO
           END IF
        END IF
     ELSE
        NULLIFY(vegtype_metfile)
     END IF
 
     ! Look for soil type:
     ok = NF90_INQ_VARID(ncid_met,'isoil',id%isoil)
     IF(ok == NF90_NOERR) THEN ! If inquiry is okay
        ! Note existence of at least one model parameter in the met file:
        exists%parameters = .TRUE.
        ! Check dimension of soil type:
        ok=NF90_INQUIRE_VARIABLE(ncid_met,id%isoil,ndims=isoil_dims)
        ! Allocate space for user-defined soil type variable:
        ALLOCATE(soiltype_metfile(mland,nmetpatches))
        ! Get soil type from met file:
        IF(metGrid=='mask') THEN
           IF(isoil_dims==2) THEN ! i.e. no patch specific isoil information
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%isoil,data2i, &
                      start=(/land_x(i),land_y(i)/),count=(/1,1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading isoil in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Set all soil patches in grid cell to be this single type
                 soiltype_metfile(i,:)=data2i(1,1)
              END DO
           ELSE IF(isoil_dims==3) THEN ! i.e. patch specific isoil information
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%isoil, &
                      soiltype_metfile(i,:), &
                      start=(/land_x(i),land_y(i),1/),count=(/1,1,nmetpatches/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading isoil in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              END DO
           END IF
        ELSE IF(metGrid=='land') THEN
           IF(isoil_dims==1) THEN ! i.e. no patch specific isoil information
              ! Collect data from land only grid in netcdf file:
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met,id%isoil,data1i, &
                      start=(/i/),count=(/1/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading isoil in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
                 ! Set all veg patches in grid cell to be this single type
                 soiltype_metfile(i,:) = data1i(1)
              END DO
           ELSE IF(isoil_dims==2) THEN ! i.e. patch specific isoil information
              DO i = 1, mland
                 ok= NF90_GET_VAR(ncid_met, id%isoil, &
                      soiltype_metfile(i,:), &
                      start=(/i,1/), count=(/1,nmetpatches/))
                 IF(ok /= NF90_NOERR) CALL nc_abort &
                      (ok,'Error reading isoil in met data file ' &
                      //TRIM(filename%met)//' (SUBROUTINE open_met_file)')
              END DO
           END IF
        END IF
     ELSE
        NULLIFY(soiltype_metfile)
     END IF
 
     ! Report finding met variables to log file:
     IF(all_met) THEN
        WRITE(logn,*) 'Found all met variables in met file.'
     ELSE
        WRITE(logn,*) 'Found all ESSENTIAL met variables in met file,', &
             ' some synthesised (as above).'
     END IF
 
    !!=================^^ End met variables search^^=======================
 END SUBROUTINE open_met_file