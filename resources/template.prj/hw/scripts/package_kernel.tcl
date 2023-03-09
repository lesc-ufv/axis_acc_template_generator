set path_to_hdl "../src/"
set path_to_packaged "./packaged_kernel_${suffix}"
set path_to_tmp_project "./tmp_kernel_pack_${suffix}"

create_project -force kernel_pack $path_to_tmp_project 
add_files -norecurse [glob $path_to_hdl/*.v $path_to_hdl/*.sv]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
ipx::package_project -root_dir $path_to_packaged -vendor xilinx.com -library RTLKernel -taxonomy /KernelIP -import_files -set_current false
ipx::unload_core $path_to_packaged/component.xml
ipx::edit_ip_in_project -upgrade true -name tmp_edit_project -directory $path_to_packaged $path_to_packaged/component.xml

set core [ipx::current_core]

set_property core_revision 2 $core
foreach up [ipx::get_user_parameters] {
  ipx::remove_user_parameter [get_property NAME $up] $core
}

for {set i 0} {$i < $num_m_axis} {incr i} {
  set n [format "%02d" $i]
  ipx::associate_bus_interfaces -busif "m${n}_axi" -clock "ap_clk" $core  
}

ipx::associate_bus_interfaces -busif "s_axi_control" -clock "ap_clk" $core

# Specify the freq_hz parameter 
set clkbif      [::ipx::get_bus_interfaces -of $core "ap_clk"]
set clkbifparam [::ipx::add_bus_parameter -quiet "FREQ_HZ" $clkbif]
# Set desired frequency                   
set_property value 250000000 $clkbifparam
# set value_resolve_type 'user' if the frequency can vary. 
set_property value_resolve_type user $clkbifparam
# set value_resolve_type 'immediate' if the frequency cannot change. 
# set_property value_resolve_type immediate $clkbifparam

set mem_map    [::ipx::add_memory_map -quiet "s_axi_control" $core]
set addr_block [::ipx::add_address_block -quiet "reg0" $mem_map]

set reg      [::ipx::add_register "CTRL" $addr_block]
  set_property description    "Control signals"    $reg
  set_property address_offset 0 $reg
  set_property size           32    $reg
  
set field [ipx::add_field AP_START $reg]
  set_property ACCESS {read-write} $field
  set_property BIT_OFFSET {0} $field
  set_property BIT_WIDTH {1} $field
  set_property DESCRIPTION {Control signal Register for 'ap_start'.} $field
  set_property MODIFIED_WRITE_VALUE {modify} $field
  
set field [ipx::add_field AP_DONE $reg]
  set_property ACCESS {read-only} $field
  set_property BIT_OFFSET {1} $field
  set_property BIT_WIDTH {1} $field
  set_property DESCRIPTION {Control signal Register for 'ap_done'.} $field
  set_property READ_ACTION {modify} $field
  
set field [ipx::add_field AP_IDLE $reg]
  set_property ACCESS {read-only} $field
  set_property BIT_OFFSET {2} $field
  set_property BIT_WIDTH {1} $field
  set_property DESCRIPTION {Control signal Register for 'ap_idle'.} $field
  set_property READ_ACTION {modify} $field
  
set field [ipx::add_field AP_READY $reg]
  set_property ACCESS {read-only} $field
  set_property BIT_OFFSET {3} $field
  set_property BIT_WIDTH {1} $field
  set_property DESCRIPTION {Control signal Register for 'ap_ready'.} $field
  set_property READ_ACTION {modify} $field
  
set field [ipx::add_field RESERVED_1 $reg]
  set_property ACCESS {read-only} $field
  set_property BIT_OFFSET {4} $field
  set_property BIT_WIDTH {3} $field
  set_property DESCRIPTION {Reserved.  0s on read.} $field
  set_property READ_ACTION {modify} $field
  
set field [ipx::add_field AUTO_RESTART $reg]
  set_property ACCESS {read-write} $field
  set_property BIT_OFFSET {7} $field
  set_property BIT_WIDTH {1} $field
  set_property DESCRIPTION {Control signal Register for 'auto_restart'.} $field
  set_property MODIFIED_WRITE_VALUE {modify} $field
  
set field [ipx::add_field RESERVED_2 $reg]
  set_property ACCESS {read-only} $field
  set_property BIT_OFFSET {8} $field
  set_property BIT_WIDTH {24} $field
  set_property DESCRIPTION {Reserved.  0s on read.} $field
  set_property READ_ACTION {modify} $field

set reg      [::ipx::add_register "GIER" $addr_block]
  set_property description    "Global Interrupt Enable Register" $reg
  set_property address_offset 4 $reg
  set_property size           32    $reg

set reg      [::ipx::add_register "IP_IER" $addr_block]
  set_property description    "IP Interrupt Enable Register"    $reg
  set_property address_offset 8 $reg
  set_property size           32    $reg

set reg      [::ipx::add_register "IP_ISR" $addr_block]
  set_property description    "IP Interrupt Status Register"    $reg
  set_property address_offset 12 $reg
  set_property size           32    $reg

set offset  16

for {set i 0} {$i < $num_m_axis} {incr i} {
  set reg      [::ipx::add_register -quiet "in_s${i}" $addr_block]
  set_property address_offset $offset $reg
  set_property size           [expr {4*8}]   $reg
  set offset [expr $offset + 8]
}

for {set i 0} {$i < $num_m_axis} {incr i} {
  set reg      [::ipx::add_register -quiet "out_s${i}" $addr_block]
  set_property address_offset $offset $reg
  set_property size           [expr {4*8}]   $reg
  set offset [expr $offset + 8]
}

for {set i 0} {$i < $num_m_axis} {incr i} {

    set n [format "%02d" $i]

    set reg      [::ipx::add_register -quiet "in${i}" $addr_block]
    set_property address_offset $offset $reg
    set_property size           [expr {8*8}]   $reg
    set regparam [::ipx::add_register_parameter -quiet {ASSOCIATED_BUSIF} $reg] 
    set_property value "m${n}_axi" $regparam
    
    set offset [expr $offset + 12]
    
    set reg      [::ipx::add_register -quiet "out${i}" $addr_block]
    set_property address_offset $offset $reg
    set_property size           [expr {8*8}]   $reg
    set regparam [::ipx::add_register_parameter -quiet {ASSOCIATED_BUSIF} $reg] 
    set_property value "m${n}_axi" $regparam
    
    set offset [expr $offset + 12]
}

  
set_property slave_memory_map_ref "s_axi_control" [::ipx::get_bus_interfaces -of $core "s_axi_control"]

set_property xpm_libraries {XPM_CDC XPM_MEMORY XPM_FIFO} $core
set_property sdx_kernel true $core
set_property sdx_kernel_type rtl $core
set_property supported_families { } $core
set_property auto_family_support_level level_2 $core
ipx::create_xgui_files $core
ipx::update_checksums $core
ipx::check_integrity -kernel $core
ipx::save_core $core
close_project -delete
