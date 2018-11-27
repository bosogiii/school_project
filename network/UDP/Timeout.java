import java.util.Timer;
import java.util.TimerTask;

/*  Timeout 관련 작업 (timer & TimeoutTask 생성, TimeoutTask 설정 및 제거) 
 *  송신 쓰래드가 보낼 것이 없을 경우 wait 하면서 송신 패킷이 있을 때까지 기다림.
 *  TimeoutTask 설정: 보낸 패킷의 seq 번호에 따라 timeout 시간을 설정해서 Timer에 설정함
 *  TimeoutTask 제거: Ack 받은 패킷의 seq 번호에 따라 timeoutTask를 Timer에서 제거함 
 */
public class Timeout {
    Timer timer = new Timer();
    TimeoutTask[] myTimerTask = new TimeoutTask[16]; //MAXSIZE
    Signaling pp;
    public int timeoutlimit = 0;
    boolean DEBUG = false;
    
    public void Timeoutset (int i, int milliseconds, Signaling p) {
    	// TimeoutTask 설정: 보낸 패킷의 seq 번호에 따라 timeout 시간을 설정해서 Timer에 설정함
    	pp = p;
    	myTimerTask[i] = new TimeoutTask(i);
        timer.schedule(myTimerTask[i], milliseconds);
	}
    
    public void Timeoutcancel (int i) {
    	// TimeoutTask 제거: Ack 받은 패킷의 seq 번호에 따라 timeoutTask를 Timer에서 제거함
    	int k=i;
    	if(DEBUG) System.out.println("Time's cancealed! no="+k);
        myTimerTask[k].cancel();
	}

    class TimeoutTask extends TimerTask {
    	int jj;
    	TimeoutTask(int j) {    		
    		jj=j;
    	}
    	public void run() {
            if(DEBUG) System.out.println( "Time's up! " + (timeoutlimit) );
            pp.Timeoutnotifying();
            this.cancel(); //Terminate the timerTask thread
        }
    }
}
