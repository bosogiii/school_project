
/**
 * Write a description of class ChatJin here.
 * 
 * @author (your name) 
 * @version (a version number or a date)
 */
import java.io.*; 
import java.net.*; 

public class UDPChatting {
	final static int MAXBUFFER = 512;
	static RcvThread rcThread; 
	public static DatagramSocket socket;
	public static InetAddress remoteaddr;
	public static InetAddress myinetaddr;
	public static boolean servermode = false;
	public static int remoteport=0, myport=0; 
	public static Signaling sig= new Signaling(); // Object를 생성해서 argument로 패싱해야 waiting/notify가 됨
	static Timeout tclick; // Timeout Interface
	public static DatagramPacket rcv_packet;

	public static void main(String[] args) {
		if(args.length == 2){
			remoteport = Integer.parseInt(args[1]);
			try {
				remoteaddr = InetAddress.getByName(args[0]);
			} catch (UnknownHostException e) {
				System.out.println("Error on port "+remoteport);
				e.printStackTrace();
			}
		} else if(args.length == 1){
		// server mode without sending first: wait for an incoming message
			myport = Integer.parseInt(args[0]); //server mode
			servermode = true;
		} else {
			System.out.println("사용법: java UDPChatting localhost port or port");
			System.exit(0);
		}
				
		try {
			if(myport==0) {socket = new DatagramSocket();}
			else 		  {socket = new DatagramSocket(myport);}
			if(servermode) {
				myinetaddr = InetAddress.getLocalHost();
				System.out.println("My address : "+ myinetaddr.getHostAddress() +", my port : "+ myport);
			}
			else{
				System.out.println("Server address : " + remoteaddr + ", port number : " + remoteport);
			}

            tclick = new Timeout();
            rcThread = new RcvThread(socket, sig);
			rcThread.start();
				
			DatagramPacket send_packet;// 송신용 데이터그램 패킷
			BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
				    
			while (true) {
				// 키보드 입력 읽기
				System.out.print("Input Data : ");
				String data;
				data = br.readLine();
				
				if (data.length() == 0){ // no char carriage return 
					System.out.println("put input!");
					continue;
				} 
				
				byte buffer[] = new byte[MAXBUFFER];
				buffer = data.getBytes();// 스트링을 바이트 배열로 바꿈
				
				// 데이터 송신
				if((remoteaddr != null)) {
					for(int i=0; i<10;i++) { // 10 times retransmission
						send_packet = new DatagramPacket (buffer, buffer.length,remoteaddr, remoteport);
						socket.send (send_packet);
						
						Signaling.TIMENOTIFY = false;
						
						tclick.Timeoutset(i, 1000, sig);
						// Timeout Start
						sig.waitingACK();
						
						/* ACKED */
						if(sig.ACKNOTIFY) {
							tclick.Timeoutcancel(0);
							break;
						} 
						
						// true: ACK,  false: Timeout
						else System.out.println("Retransmission "+data);
					}
				} else   System.out.println("Server mode: unable to send until receive packet");
			}
				
		} catch(IOException e) {
			System.out.println(e);
		}
		
		rcThread.graceout(); // grace exit of Receive Thread 
		System.out.println("grace out called");
		socket.close();
	}
}

