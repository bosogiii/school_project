import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;

class RcvThread extends Thread {
	final static int MAXBUFFER = 512;
	DatagramSocket socket;
	boolean	sem = true;
	DatagramPacket rcv_packet;// 수신용 데이터그램 패킷
	public Signaling sig;
	
	//쓰레드 생성자
	RcvThread (DatagramSocket s, Signaling pp) {
		socket = s;
		sig=pp; // should be defined (정의 안되면 null point exception 발생)
	}
	
	public void run() {
			byte buff[] = new byte[MAXBUFFER];
			rcv_packet = new DatagramPacket (buff, buff.length);
			
		while (sem) {
			try {
		       socket.receive(rcv_packet);
		       UDPChatting.remoteport = rcv_packet.getPort();// 임의의 소켓에 대한 응답을 위해
		       UDPChatting.remoteaddr = rcv_packet.getAddress();// 임의의 소켓에 대한 응답을 위해
			} catch(IOException e) {
				e.printStackTrace();
			}

			String result = new String(buff);
			result = result.trim();
			
			boolean isACK = true;
			
			for(int i = 0; i < 5; i++) {
				if(buff[i] != i + 1) {
					isACK = false;
					break;
				}
			
			}
			
			if(isACK)
				System.out.println("ACK arrived.");
			else
				System.out.println("Receive Data : " + result); 

			if(!isACK) {
				try{
					byte ack[] = {1, 2, 3, 4, 5};
					socket.send(new DatagramPacket(ack, ack.length, rcv_packet.getAddress(), rcv_packet.getPort()));
				} catch(IOException e){
					e.printStackTrace();
				}
			}
			
			for(int i = 0; i < buff.length; i++)
				buff[i] = 0;
			
			sig.ACKnotifying();
			/* ACKED */
		}
		
		System.out.println("grace out");
	}
	public void graceout(){
		sem = false;
	}
			
} // end ReceiverThread class
