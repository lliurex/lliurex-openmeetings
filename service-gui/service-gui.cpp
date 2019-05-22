#include <iostream>
#include <fstream>
#include <cstdio>

#include <map>
#include <vector>

#include <gtkmm.h>
#include <glibmm.h>

#include <libintl.h>
#include <locale.h>

#define T(String) gettext(String) 

#define CMD_SERVICE_CHECK "lliurex-openmeetings-service status"
#define CMD_SERVICE_START "lliurex-openmeetings-service start"
#define CMD_SERVICE_STOP "lliurex-openmeetings-service stop"


using namespace std;


/**
 * Application class
 */
class Application
{
	private:
	
	Glib::RefPtr<Gtk::Builder> glade;
	Gtk::Window * winService;
	Gtk::Switch * sw;
	Gtk::Label * lblStatus;
	Gtk::Button * btnOk;
	
	Glib::Dispatcher signal_service_started;
	Glib::Dispatcher signal_service_stoped;
	
	public:
	
	/**
	 * Constructor
	 */ 
	Application()
	{
		string glade_path;
		
		if(Gio::File::create_for_path("interface.glade")->query_exists())
		{
			glade_path="interface.glade";
		}
		else
		{
			if(Gio::File::create_for_path("/usr/share/lliurex-openmeetings/service-rsrc/interface.glade")->query_exists())
			{
				glade_path="/usr/share/lliurex-openmeetings/service-rsrc/interface.glade";
			}
			else
			{
				cerr<<"Can't find glade resource"<<endl;
				std::exit(1);
			}
			
		}
		cout<<"* Using glade resource:"<<glade_path<<endl;
		
		glade=Gtk::Builder::create_from_file(glade_path);
		glade->get_widget("winService",winService);
		
		winService->signal_delete_event().connect(sigc::mem_fun(*this,&Application::OnWinServiceClose));
		
		glade->get_widget("lblStatus",lblStatus);
		glade->get_widget("switchStatus",sw);
		
		/* we check first current service status */
		UpdateWidgets(CheckService());
		
		
		
		sw->property_active().signal_changed().connect(sigc::mem_fun(*this,&Application::OnSwitchServiceChanged));
		
		
		glade->get_widget("btnOk",btnOk);
		btnOk->signal_clicked().connect(sigc::mem_fun(*this,&Application::OnBtnOkClick));
		
		signal_service_started.connect(sigc::mem_fun(*this,&Application::OnServiceStarted));
		signal_service_stoped.connect(sigc::mem_fun(*this,&Application::OnServiceStoped));
		
		
		winService->show_all();
	}
	
	/**
	 * Destructor
	 */ 
	~Application()
	{
		
	}
	
	/**
	 * Window close hook
	 */ 
	bool OnWinServiceClose(GdkEventAny* event)
	{
		Gtk::Main::quit();
		return true;
	}
	
	/**
	 * Switch state hook
	 */ 
	void OnSwitchServiceChanged()
	{
		
		
		if(sw->get_active())
		{
			cout<<"* Starting Openmeetings service..."<<endl;
			sw->set_sensitive(false);
			btnOk->set_sensitive(false);
			lblStatus->set_text(T("Starting..."));
			Glib::Thread::create(sigc::mem_fun(*this, &Application::StartService));			
		}
		else
		{
			cout<<"* Stoping Openmeetings service..."<<endl;
			sw->set_sensitive(false);
			btnOk->set_sensitive(false);
			lblStatus->set_text(T("Stoping..."));
			Glib::Thread::create(sigc::mem_fun(*this, &Application::StopService));			
		}
	}
	
	/**
	 * Button Ok Click
	 */ 
	void OnBtnOkClick()
	{
		Gtk::Main::quit();
	}
	
	
	/**
	 * Service started hook
	 */
	void  OnServiceStarted()
	{
		cout<<"* Service start completed"<<endl;
		
		btnOk->set_sensitive(true);
		sw->set_sensitive(true);
		UpdateWidgets(CheckService());
	}

	/**
	* Service stopt hook
	*/ 
	void OnServiceStoped()
	{
		cout<<"* Service stop completed"<<endl;
		
		btnOk->set_sensitive(true);
		sw->set_sensitive(true);
		UpdateWidgets(CheckService());
	}
	
	
	/**
	 * Checks whenever openmeeting is running or not
	 * \returns true if it is running, false elsewhere
	 */ 
	bool CheckService()
	{
		int status;
		string err;
		string out;
		
		/* ToDo: replace with the proper command */
		Glib::spawn_command_line_sync(CMD_SERVICE_CHECK,&out,&err,&status);
		
		cout<<"status:"<<status<<endl;
		cout<<"out:"<<out<<endl;
		
		return (out=="RUNNING\n");
	}
	
	/**
	 * Service start thread
	 */ 
	void StartService()
	{
		int status;
		string err;
		string out;
		
		/* ToDo: replace with the proper command */			
		Glib::spawn_command_line_sync(CMD_SERVICE_START,&out,&err,&status);
		
		signal_service_started();
	}
	
	
	
	/**
	 * Service stop thread
	 */ 
	void StopService()
	{
		
		int status;
		string err;
		string out;
		
		/* ToDo: replace with the proper command */
		Glib::spawn_command_line_sync(CMD_SERVICE_STOP,&out,&err,&status);
		
		signal_service_stoped();
	}
	
	
	void UpdateWidgets(bool is_running)
	{
		if(is_running)
		{
			lblStatus->set_text(T("Running"));
			sw->set_active(is_running);
		}
		else
		{
			lblStatus->set_text(T("Stopped"));
			sw->set_active(is_running);
		}
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
