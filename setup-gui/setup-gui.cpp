
#include <iostream>
#include <fstream>
#include <cstdio>

#include <map>
#include <vector>
#include <deque>

#include <gtkmm.h>
#include <glibmm.h>


#include <libintl.h>
#include <locale.h>

#include <sys/wait.h>

#define T(String) gettext(String) 


using namespace std;


/**
 * Application class
 */
class Application
{
	private:
	
	Glib::RefPtr<Gtk::Builder> glade;
	Gtk::Window * winInit;
	Gtk::Window * winProgress;
	Gtk::Window * winMessage;
	Gtk::ProgressBar * pbarInitializing;
	
	Gtk::TextView * viewConsole;
	
	Glib::Mutex text_buffer_mutex;
	deque<string> text_buffer;
	Glib::Dispatcher signal_output_available;
		
	bool spawn_completed;
	int spawn_status;
	
	public:
	
	/**
	 * Constructor
	 */ 
	Application()
	{
		cout<<"* Welcome to lliurex openmeetings"<<endl;
		
		spawn_completed=false;
		spawn_status=0;
		
		string glade_path;
		
		if(Gio::File::create_for_path("interface.glade")->query_exists())
		{
			glade_path="interface.glade";
		}
		else
		{
			if(Gio::File::create_for_path("/usr/share/lliurex-openmeetings/service-rsrc/interface.glade")->query_exists())
			{
				glade_path="/usr/share/lliurex-openmeetings/setup-rsrc/interface.glade";
			}
			else
			{
				cerr<<"Can't find glade resource"<<endl;
				std::exit(1);
			}
			
		}
		cout<<"* Using glade resource:"<<glade_path<<endl;
		
		glade=Gtk::Builder::create_from_file(glade_path);
		glade->get_widget("winInit",winInit);
		glade->get_widget("winProgress",winProgress);
		glade->get_widget("winMessage",winMessage);
		
		glade->get_widget("pbarInitializing",pbarInitializing);
		glade->get_widget("viewConsole",viewConsole);
		
		winInit->signal_delete_event().connect(sigc::mem_fun(*this,&Application::OnWinInitClose));
		
		Gtk::Button * button;
		glade->get_widget("btnInit",button);
		button->signal_clicked().connect(sigc::mem_fun(*this,&Application::OnBtnInitClick));
		
		glade->get_widget("btnMessageOk",button);
		button->signal_clicked().connect(sigc::mem_fun(*this,&Application::OnBtnMessageOkClick));
		
		Glib::signal_timeout().connect(sigc::mem_fun(*this,&Application::OnTimer), 500);
		
		signal_output_available.connect(sigc::mem_fun(*this,&Application::OnOutputAvailable));
		
		winInit->show_all();	
	}
	
	/**
	 * Destructor
	 */ 
	~Application()
	{
		cout<<"* bye"<<endl;
	}
	
	/**
	 * Init window close hook
	 */ 
	bool OnWinInitClose(GdkEventAny* event)
	{
		cout<<"* Close signal catched!"<<endl;
		Gtk::Main::quit();
		return true;
	}
	
	/**
	 * Init button hook
	 */ 
	void OnBtnInitClick()
	{
		map<string,string> data;
		bool is_ok=true;
		
		cout<<"* initializing..."<<endl;
		
		/* checking values */
		
		Gtk::Entry * txtDBUser;
		Gtk::Entry * txtDBPass;
		Gtk::Entry * txtDBPass2;
		
		Gtk::Entry * txtAdminUser;
		Gtk::Entry * txtAdminPass;
		Gtk::Entry * txtAdminPass2;
		
		Gtk::Entry * txtEmail;
		
		
		Gtk::Label * lblWarning;
		glade->get_widget("lblWarning",lblWarning);
		
		glade->get_widget("txtDBUser",txtDBUser);
		glade->get_widget("txtDBPass",txtDBPass);
		glade->get_widget("txtDBPass2",txtDBPass2);
		
		glade->get_widget("txtAdminUser",txtAdminUser);
		glade->get_widget("txtAdminPass",txtAdminPass);
		glade->get_widget("txtAdminPass2",txtAdminPass2);
		
		glade->get_widget("txtEmail",txtEmail);
		
		
		data["db_user"]=txtDBUser->get_text();
		data["db_pass"]=txtDBPass->get_text();
		
		
		data["admin"]=txtAdminUser->get_text();
		data["password"]=txtAdminPass->get_text();
				
		data["email"]=txtEmail->get_text();
		
		try
		{
			if(data["db_user"]=="root")throw string(T("root is not a valid database user"));
			if(data["db_user"].length()<4)throw string(T("Database user should have at least, four characters"));
			
			if(data["db_pass"].length()<4)throw string(T("Database password should have at least, four characters"));
			if(data["db_pass"]!=txtDBPass2->get_text())throw string(T("Database passwords do not match"));
			
			if(data["admin"].length()<4)throw string(T("Admin user should have at least, four characters"));
			
			if(data["password"].length()<4)throw string(T("Admin password should have at least, four characters"));
			if(data["password"]!=txtAdminPass2->get_text())throw string(T("Admin passwords do not match"));
			
			/* I had a problem, I used regex. Now I have two problems 
			 * Following regex expression checks whenever is a valid email address...
			 * at least it was designed with that in mind
			 * */
			Glib::RefPtr<Glib::Regex> regex = Glib::Regex::create("^[[:alnum:]_]+@[[:alnum:]]+\\.[[:alnum:]]+(\\.[[:alnum:]]+)*$");	
			
			if(!regex->match(data["email"]))throw string(T("Invalid email address"));
			
		}
		catch(string & e)
		{
			lblWarning->set_text(e);
			is_ok=false;
		}
		
		
				
		
		
		
		/* if settings are ok we can Initialize openmeetings and wait patiently */
		if(is_ok)
		{
			lblWarning->set_text("");
			
			WriteSetup(data);
			
			winInit->hide();
			winProgress->show_all();
			
			spawn_completed=false;			
						
			Glib::Thread::create(sigc::mem_fun(*this, &Application::SubProcess));			
		}
		
	}
	
	/**
	 * Message button hook
	 */ 
	void OnBtnMessageOkClick()
	{
		Gtk::Main::quit();
	}
	
	
	/**
	 * Timer Tick
	 */ 
	int OnTimer()
	{
		
		/* once process is gone, we show message window and stop this timer */
		if(spawn_completed)
		{
			
						
			/* message box is customized in case of wrong output status */
			if(spawn_status!=0)
			{
				Gtk::Label * lblMessage;
				glade->get_widget("lblMessage",lblMessage);
				
				Gtk::Image * imgMessage;
				glade->get_widget("imgMessage",imgMessage);
											
				lblMessage->set_text(T("There was an error while setting openmeetings up, check output for details"));
				imgMessage->set_from_icon_name("dialog-error",Gtk::IconSize(Gtk::ICON_SIZE_DIALOG));
				
			}
			
			winMessage->show_all();
			
			return 0;
		}
		
		pbarInitializing->pulse();
		return 1;
	}
	
	
	
	/**
	 * Writes setup file to /tmp
	 */ 
	void WriteSetup(map<string,string> & data)
	{
		ofstream file;
		file.open ("/tmp/lliurex-openmeetings.conf");
		file << "[openmeetings]\n";
		
		for(pair<const string,string> & node : data)
		{
			file<<node.first<<"="<<node.second<<"\n";
		}
		
		file.close();
	}
		
	/**
	* This signal is invoked whenever a new line has come through the pipe
	* the line is dequed from the queue and pushed into the TextBuffer
	*/
	void OnOutputAvailable()
	{
		text_buffer_mutex.lock();
		string text = text_buffer.front();
		text_buffer.pop_front();
		text_buffer_mutex.unlock();
		
		
		Gtk::TextIter it = viewConsole->get_buffer()->end();
		it=viewConsole->get_buffer()->insert(it,text);
		viewConsole->scroll_to(it);
	}
	
	/**
	 * Spawns initialization script (from a thread)
	 */ 
	void SubProcess()
	{
		/* credits goes for: R Samuel Klatchko
		 * from StackOverflow
		 * */
		 
		int pipefd[2];
		int r=pipe(pipefd);
		
		if(r==-1)
		{
			cerr<<"* Failed to create pipe"<<endl;
			exit(4);
		}
		
		int pid = fork();
		
		if(pid<0)
		{
			cerr<<"* Failed to fork child process "<<endl;
			exit(3);
		}
		
		if (pid == 0)
		{
			close(pipefd[0]);    // close reading end in the child

			dup2(pipefd[1], 1);  // send stdout to the pipe
			dup2(pipefd[1], 2);  // send stderr to the pipe

			close(pipefd[1]);    // this descriptor is no longer needed
			
			/* yes, I'm using magic string constants */
			int status=execl("/usr/sbin/lliurex-openmeetings","lliurex-openmeetings","-t","/tmp/lliurex-openmeetings.conf",NULL);
			
			/* In case of fail, we just exit the application with an error status */
			if(status==-1)
			{
				cerr<<"* Failed to spawn child process "<<endl;
				exit(3);
			}
		}
		else
		{
			char c;
			string line;

			close(pipefd[1]);  // close the write end of the pipe in the parent

			while (read(pipefd[0], &c, 1) != 0)
			{
				
				line=line+c;
				
				/* we read characters until complete a line 
				 then, the line is pushed into TextBuffer
				*/
				if(c=='\n')
				{
				
					
					text_buffer_mutex.lock();
					text_buffer.push_back(line);
					text_buffer_mutex.unlock();
					
					signal_output_available();
					
					line="";
				}
				
				
			}
		}
		
		
		
		
			
		waitpid(pid,&spawn_status,0);
		
		spawn_completed=true;
		
		cout<<"* process completed"<<endl;
		
		
		
	}
	
};

int main(int argc,char * argv[])
{
	
	textdomain("lliurex-openmeetings-setup");
	Gtk::Main kit(argc, argv);
	Application app;
	Gtk::Main::run();

	return 0;
}
